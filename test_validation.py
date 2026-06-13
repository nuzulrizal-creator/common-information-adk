import os
import google.generativeai as genai
from ai_agent_router import product_recommendation_tool, common_information_tool

# Pastikan API Key diatur
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_ANDA")
genai.configure(api_key=GEMINI_API_KEY)

def run_tests():
    system_instruction = """
    Kamu adalah 'SmartShopper Assistant'.
    Gunakan 'product_recommendation_tool' JIKA user menanyakan tentang produk.
    Gunakan 'common_information_tool' JIKA user menanyakan informasi umum/FAQ operasional toko.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[product_recommendation_tool, common_information_tool],
        system_instruction=system_instruction
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    test_cases = [
        # Tes 1: Produk
        "Tolong carikan sepatu lari merk Nike warna hitam ukuran 42.",
        # Tes 2: Produk
        "Berapa harga Samsung Galaxy S24 Ultra sekarang?",
        # Tes 3: Common Info
        "Berapa lama proses pengiriman barang reguler?",
        # Tes 4: Common Info
        "Pesanan saya dibatalkan, kira-kira kapan uang refund saya kembali ke rekening bank?",
        # Tes 5: Edge Case (Gabungan)
        "Saya mau beli iPhone 15, tapi apa bisa bayar secara COD?"
    ]
    
    print("=========================================================")
    print("🔍 MEMULAI PENGUJIAN OTOMATIS AI AGENT ROUTING")
    print("=========================================================\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"--- TEST CASE {i} ---")
        print(f"User Query: {query}")
        try:
            # Karena enable_automatic_function_calling=True, print() di dalam tool akan 
            # memberitahu kita tool mana yang terpanggil oleh AI.
            response = chat.send_message(query)
            print(f"Jawaban AI: {response.text}\n")
        except Exception as e:
            print(f"Error pada Test Case {i}: {e}\n")
            
    print("✅ PENGUJIAN SELESAI.")

if __name__ == "__main__":
    run_tests()
