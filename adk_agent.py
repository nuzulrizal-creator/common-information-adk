import os
from google.adk.agents.llm_agent import Agent

# Import pipeline pencarian yang sudah kita bangun
from rag_implementation import retrieve_context, generate_answer

# ==========================================
# 1. TOOL: Product Recommendation
# ==========================================
def product_recommendation_tool(query: str) -> dict:
    """
    Gunakan tool ini JIKA DAN HANYA JIKA pengguna menanyakan tentang spesifikasi produk, 
    rekomendasi produk, harga barang, atau ketersediaan stok barang.
    
    Args:
        query: Kata kunci produk yang dicari oleh user.
    """
    print(f"\n[ADK Routing] -> Menjalankan Product Tool untuk query: '{query}'")
    # Mock data (seolah-olah mengambil dari database produk)
    return {
        "status": "success", 
        "query": query, 
        "result": "Menampilkan daftar produk yang relevan..."
    }

# ==========================================
# 2. TOOL: Common Information
# ==========================================
def common_information_tool(query: str) -> str:
    """
    Gunakan tool ini JIKA DAN HANYA JIKA pengguna menanyakan tentang operasional toko,
    seperti kebijakan pengiriman, metode pembayaran (COD/Transfer), prosedur refund, retur, 
    atau masalah teknis akun pengguna. JANGAN gunakan untuk mencari nama produk.
    
    Args:
        query: Pertanyaan seputar FAQ/kebijakan operasional.
    """
    print(f"\n[ADK Routing] -> Menjalankan Common Information Tool untuk query: '{query}'")
    
    # Memanggil RAG (Retrieval-Augmented Generation) dari database MongoDB
    context = retrieve_context(query)
    
    if not context:
        return "Sistem tidak dapat menemukan informasi relevan di database FAQ."
        
    answer = generate_answer(query, context)
    return answer

# ==========================================
# 3. SETUP ADK AGENT
# ==========================================
# Inisialisasi Root Agent dari Google ADK
smartshopper_agent = Agent(
    model='gemini-1.5-flash',
    name='SmartShopper_Assistant',
    description="Asisten e-commerce yang melayani pembelian produk dan pertanyaan operasional.",
    instruction="""
    Kamu adalah 'SmartShopper Assistant', asisten AI e-commerce yang ramah.
    
    ATURAN ROUTING:
    Kamu memiliki dua tool yang wajib digunakan sesuai dengan niat pengguna:
    1. 'product_recommendation_tool': Panggil ini untuk mencari barang, harga, atau spesifikasi produk.
    2. 'common_information_tool': Panggil ini untuk prosedur layanan (COD, pengiriman, refund, retur, dsb).
    
    Kamu tidak boleh mengarang jawaban terkait kebijakan atau produk tanpa memanggil tool.
    """,
    tools=[product_recommendation_tool, common_information_tool]
)

if __name__ == "__main__":
    print("=========================================================")
    print("SmartShopper ADK Agent Aktif (Ketik 'keluar' untuk stop)")
    print("=========================================================\n")
    
    while True:
        user_input = input("Anda: ")
        if user_input.lower() in ['keluar', 'exit', 'quit']:
            break
            
        try:
            # Mengeksekusi ADK Agent dengan input pengguna secara asynchronous
            import asyncio
            response = asyncio.run(smartshopper_agent.run(user_input))
            print(f"SmartShopper: {response}\n")
        except Exception as e:
            print(f"[Error]: {e}\n")
