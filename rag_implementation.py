import os
from pymongo import MongoClient
import google.generativeai as genai

# ==========================================
# Konfigurasi Database & API
# ==========================================
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb+srv://nuzulrizalnr_db_user:password123.@cluster0.e8mptlb.mongodb.net/?appName=Cluster0")
DB_NAME = "smartshopper_db"
COLLECTION_NAME = "common_information"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_ANDA")
genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 1. GENERATE & STORE EMBEDDINGS (Persiapan RAG)
# ==========================================
def embed_and_store_data():
    """
    Fungsi ini dijalankan SEKALI untuk mengubah teks FAQ menjadi Vector (Embedding)
    dan menyimpannya ke dalam dokumen MongoDB.
    """
    client = MongoClient(MONGO_URI)
    collection = client[DB_NAME][COLLECTION_NAME]
    
    docs = list(collection.find({}))
    print(f"Membuat embeddings untuk {len(docs)} dokumen...")
    
    for doc in docs:
        # Menggabungkan Q&A sebagai satu teks untuk di-embed
        text_to_embed = f"Topik: {doc.get('topic')}\nPertanyaan: {doc.get('question')}\nJawaban: {doc.get('answer')}"
        
        # Mendapatkan vector dari model embedding Gemini
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text_to_embed,
            task_type="retrieval_document"
        )
        embedding_vector = result['embedding']
        
        # Update MongoDB dengan field 'embedding' dan 'content_text'
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": embedding_vector, "content_text": text_to_embed}}
        )
    print("Berhasil menyimpan embeddings ke MongoDB Atlas.")
    print(">> PENTING: Anda HARUS membuat Vector Search Index bernama 'vector_index' di Atlas UI <<")

# ==========================================
# 2. RETRIEVAL (Mencari konteks yang relevan)
# ==========================================
def retrieve_context(query: str, top_k: int = 2) -> str:
    """Menggunakan MongoDB Atlas Vector Search untuk mencari FAQ terdekat dengan query."""
    client = MongoClient(MONGO_URI)
    collection = client[DB_NAME][COLLECTION_NAME]
    
    # Jadikan query pengguna sebagai vector
    query_result = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query"
    )
    query_vector = query_result['embedding']
    
    # Aggregation Pipeline untuk Vector Search
    # Pastikan index 'vector_index' telah dibuat di cluster Atlas Anda.
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", 
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 10,
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "content_text": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]
    
    try:
        results = list(collection.aggregate(pipeline))
        context_str = "\n\n".join([doc['content_text'] for doc in results])
        return context_str
    except Exception as e:
        print(f"Error Vector Search: {e}")
        return ""

# ==========================================
# 3. GENERATION (Menghasilkan jawaban AI)
# ==========================================
def generate_answer(query: str, context: str) -> str:
    """Menghasilkan jawaban menggunakan Gemini berdasarkan Konteks Retrieval."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Kamu adalah asisten e-commerce yang cerdas dan sangat membantu.
    Tugas utamamu adalah menjawab pertanyaan pengguna menggunakan informasi dari Konteks berikut.
    Jika di dalam konteks tidak ada informasi yang relevan, dengan sopan katakan bahwa kamu belum 
    memiliki informasinya dan arahkan ke Customer Service.
    
    [KONTEKS]
    {context}
    
    [PERTANYAAN PENGGUNA]
    {query}
    """
    
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 4. RAG PIPELINE
# ==========================================
def run_rag_pipeline(query: str):
    print(f"\n--- Menjalankan RAG Pipeline ---")
    print(f"Query User: '{query}'")
    
    print("\n[Tahap 1] Melakukan Retrieval...")
    context = retrieve_context(query)
    
    if not context:
        print("Gagal mengambil konteks. Harap pastikan Embeddings sudah disimpan dan Vector Index dibuat di Atlas.")
        return
    
    print("[Tahap 2] Melakukan Generation...")
    answer = generate_answer(query, context)
    
    print("\n===== JAWABAN AI =====")
    print(answer)
    print("======================")

if __name__ == "__main__":
    # CARA PENGGUNAAN:
    
    # LANGKAH A: Hapus tanda pagar (uncomment) pada baris di bawah ini dan jalankan SEKALI
    # untuk menyimpan embedding ke MongoDB. Setelah itu, buat Index di Atlas UI.
    # embed_and_store_data()
    
    # LANGKAH B: Setelah Index selesai dibuat, Anda bisa menguji RAG
    # query_test = "Kalau batal pesan, kapan uang refund kembali?"
    # run_rag_pipeline(query_test)
    pass
