import os
from pymongo import MongoClient
import google.generativeai as genai

# ==========================================
# Konfigurasi Database MongoDB
# ==========================================
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb+srv://nuzulrizalnr_db_user:password123.@cluster0.e8mptlb.mongodb.net/?appName=Cluster0")
DB_NAME = "smartshopper_db"
COLLECTION_NAME = "common_information"

# Pastikan API Key Google Gemini sudah di-set di environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_ANDA")
genai.configure(api_key=GEMINI_API_KEY)

def get_common_information(query: str) -> str:
    """
    Tool ini digunakan untuk mencari informasi umum (FAQ) terkait prosedur toko, 
    kebijakan pengiriman, pembayaran, pengembalian/retur (refund), dan operasional akun.
    
    Args:
        query (str): Pertanyaan spesifik dari pengguna terkait informasi umum.
    """
    print(f"--> [Tool Executed] Mencari informasi untuk query: '{query}'")
    
    # ---------------------------------------------------------
    # 1. PROSES RETRIEVAL (Pengambilan Data dari MongoDB)
    # ---------------------------------------------------------
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Mengambil semua data Common Information sebagai basis pengetahuan
    # (Jika dataset sangat besar, disarankan menggunakan MongoDB Atlas Vector Search)
    cursor = collection.find({}, {"_id": 0})
    faq_data = list(cursor)
    
    # Memformat data hasil retrieve menjadi sebuah konteks teks panjang
    context_str = ""
    for item in faq_data:
        context_str += f"Kategori: {item.get('category')}\n"
        context_str += f"Q: {item.get('question')}\n"
        context_str += f"A: {item.get('answer')}\n\n"
        
    if not context_str:
        return "Mohon maaf, data informasi umum saat ini sedang tidak tersedia di database."

    # ---------------------------------------------------------
    # 2. PROSES GENERATION (Pembuatan Jawaban dengan LLM)
    # ---------------------------------------------------------
    # Menggunakan LLM untuk membaca hasil retrieval dan menjawab pertanyaan user
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Kamu adalah asisten e-commerce yang cerdas dan ramah. 
    Tugasmu adalah menjawab pertanyaan pengguna HANYA berdasarkan konteks FAQ di bawah ini.
    Jika jawabannya tidak ada di dalam konteks, katakan bahwa kamu tidak memiliki informasi tersebut 
    dan arahkan pengguna untuk menghubungi Customer Service.

    Konteks FAQ:
    {context_str}

    Pertanyaan Pengguna: {query}
    
    Jawaban:
    """
    
    response = model.generate_content(prompt)
    return response.text


# =====================================================================
# INTEGRASI KE FUNCTION TOOL (Contoh untuk LlamaIndex atau SDK lainnya)
# =====================================================================
if __name__ == "__main__":
    # Jika Anda menggunakan LlamaIndex (atau framework yang menggunakan FunctionTool):
    try:
        from llama_index.core.tools import FunctionTool
        
        # Membuat FunctionTool dari fungsi python di atas
        common_info_tool = FunctionTool.from_defaults(
            fn=get_common_information,
            name="common_information_tool",
            description="Gunakan tool ini HANYA untuk menjawab pertanyaan seputar pengiriman, pembayaran, refund, dan kebijakan toko."
        )
        print("FunctionTool 'common_information_tool' berhasil dibuat!")
        
        # Contoh Uji Coba Langsung (Testing the Tool)
        print("\n--- Menguji Tool ---")
        test_query = "Bagaimana cara membatalkan pesanan yang belum dibayar?"
        hasil = common_info_tool(test_query)
        print(f"Pertanyaan: {test_query}")
        print(f"Jawaban: {hasil.raw_output}")

    except ImportError:
        print("LlamaIndex tidak terinstall. Jalankan 'pip install llama-index' jika ingin menggunakan FunctionTool dari LlamaIndex.")
        
        # Uji coba fungsi reguler (tanpa LlamaIndex)
        print("\n--- Menguji Fungsi Biasa ---")
        hasil = get_common_information("Apakah bisa bayar pakai COD?")
        print(hasil)
