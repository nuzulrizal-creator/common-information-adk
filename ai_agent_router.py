import os
import google.generativeai as genai

# ==========================================
# 1. TOOL: Product Recommendation
# ==========================================
# (Ini merupakan placeholder/mock-up jika Anda memiliki file tool product sebelumnya, 
# Anda dapat meng-import fungsinya ke sini)
def product_recommendation_tool(query: str) -> str:
    """
    Gunakan tool ini JIKA DAN HANYA JIKA pengguna menanyakan tentang produk.
    Misalnya: mencari barang, minta rekomendasi produk, spesifikasi barang, ketersediaan stok, harga, dsb.
    
    Args:
        query: Kata kunci atau detail produk yang dicari.
    """
    print(f"\n[Sistem] 🔄 Melakukan routing ke PRODUCT RECOMMENDATION TOOL untuk query: '{query}'")
    # Di implementasi asli Anda:
    # from product_tool import get_product_recommendation
    # return get_product_recommendation(query)
    
    return f"Data dummy: Menampilkan rekomendasi produk teratas untuk pencarian '{query}'..."

# ==========================================
# 2. TOOL: Common Information (RAG)
# ==========================================
def common_information_tool(query: str) -> str:
    """
    Gunakan tool ini JIKA DAN HANYA JIKA pengguna bertanya tentang informasi operasional, 
    layanan pelanggan, aturan, atau FAQ. Misalnya: pengiriman, lacak resi, metode bayar,
    COD, prosedur retur/refund, atau cara ubah akun. JANGAN gunakan untuk mencari produk.
    
    Args:
        query: Pertanyaan seputar kebijakan dan FAQ operasional e-commerce.
    """
    print(f"\n[Sistem] 🔄 Melakukan routing ke COMMON INFORMATION TOOL untuk query: '{query}'")
    
    # Import pipeline RAG yang sudah kita buat sebelumnya
    # Catatan: pastikan file rag_implementation.py ada di folder yang sama
    try:
        from rag_implementation import retrieve_context, generate_answer
        context = retrieve_context(query)
        if not context:
            return "Informasi tidak ditemukan di database FAQ. Arahkan pengguna ke Customer Service."
        
        answer = generate_answer(query, context)
        return answer
    except Exception as e:
        return f"Terjadi kesalahan saat memanggil Common Info RAG: {str(e)}"

# ==========================================
# 3. AI AGENT DENGAN ROUTING & SYSTEM PROMPT
# ==========================================
def main_chat_agent():
    # Pastikan API Key diatur di sistem atau ubah "MASUKKAN_API_KEY_ANDA"
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_ANDA")
    genai.configure(api_key=GEMINI_API_KEY)

    # Mengatur System Prompt untuk menginstruksikan mekanisme Routing
    system_instruction = """
    Kamu adalah 'SmartShopper Assistant', sebuah AI cerdas untuk platform e-commerce.
    Tugasmu adalah membantu pelanggan berbelanja dan menyelesaikan masalah operasional mereka.
    
    ATURAN ROUTING (FUNCTION CALLING) SANGAT PENTING:
    Kamu memiliki 2 alat (tools). Kamu WAJIB menggunakan tool yang tepat berdasarkan pertanyaan user:
    1. 'product_recommendation_tool': Panggil ini JIKA pengguna bertanya spesifik tentang PRODUK (Beli apa?, Rekomendasi sepatu, spek laptop, bedanya HP A dan B).
    2. 'common_information_tool': Panggil ini JIKA pengguna bertanya seputar LAYANAN TOKO (Bisa COD?, Berapa lama kirim?, Cara tukar barang?, Kapan uang refund cair?).
    
    Jika pertanyaan pengguna tidak jelas, bertanyalah kembali untuk klarifikasi sebelum memanggil tool.
    Jawablah pengguna menggunakan informasi hasil dari tool tersebut dengan ramah, natural, dan sopan.
    """

    # Menggunakan model pro atau flash yang mensupport Function Calling (Tools)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[product_recommendation_tool, common_information_tool],
        system_instruction=system_instruction
    )
    
    # enable_automatic_function_calling = True membuat AI secara otomatis:
    # 1. Mendeteksi butuh tool mana -> 2. Menjalankan fungsi python-nya -> 3. Menerima hasil -> 4. Memberikan jawaban final.
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    print("=========================================================")
    print("🛍️  SmartShopper AI Agent Aktif (Ketik 'keluar' untuk stop)")
    print("=========================================================\n")
    
    while True:
        user_input = input("Anda: ")
        if user_input.lower() in ['keluar', 'exit', 'quit']:
            print("SmartShopper: Terima kasih telah berbelanja! Sampai jumpa.")
            break
            
        try:
            response = chat.send_message(user_input)
            print(f"SmartShopper: {response.text}\n")
        except Exception as e:
            print(f"[Error Routing/Agent]: {e}\n")

if __name__ == "__main__":
    main_chat_agent()
