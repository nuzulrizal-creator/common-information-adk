# SmartShopper Assistant - Final Project Day 50

Repository ini berisi implementasi tugas akhir pembuatan *AI Agent Router* cerdas dengan kemampuan RAG (Retrieval-Augmented Generation) menggunakan **Google ADK** dan **MongoDB Atlas**.

## Ekspektasi Output & Solusi

### 1. Repository Github berisi source code lengkap dan terstruktur
Semua *source code* telah disusun dengan rapi dan modular:
*   `common_information.json` : Dataset mentah FAQ/Kebijakan operasional.
*   `store_to_mongodb.py` : Program untuk memasukkan data ke *database*.
*   `rag_implementation.py` : Fungsi RAG (Embedding, Retrieval, Generation).
*   `adk_agent.py` : Program Utama Agent menggunakan *framework* Google ADK.
*   `requirements.txt` : Daftar *library* yang diperlukan (Google ADK, pymongo, dll).

### 2. Program storing data ke MongoDB Atlas beserta penjelasan singkat
Program ini ada di file **`store_to_mongodb.py`**. 
**Penjelasan Singkat Strategi Penyimpanan:**
> Data FAQ dari file `common_information.json` dibaca terlebih dahulu menggunakan Python. Setelah itu, kode melakukan koneksi ke kluster MongoDB Atlas milik pengguna melalui *Connection String* URI. Strategi yang digunakan adalah menghapus seluruh data lama di *collection* (`delete_many`) untuk mencegah duplikasi, lalu memasukkan *batch* data baru secara serentak (`insert_many`). Setiap dokumen JSON langsung dipetakan menjadi sebuah dokumen NoSQL (BSON) di MongoDB.

### 3. Tools Common Information yang terintegrasi dengan AI Agent
Modul *Retrieval* dan *Generation* telah dikemas menjadi satu fungsi utuh bernama `common_information_tool` di dalam file **`adk_agent.py`**. Tool ini terhubung dengan RAG dan di- *import* langsung ke dalam objek `Agent()` dari Google ADK bersama dengan *product tool*.

### 4. AI Agent mampu melakukan routing tools secara otomatis berdasarkan pertanyaan user
Terletak di file **`adk_agent.py`**. Otak dari sistem menggunakan `google.adk.agents.llm_agent.Agent`. Di sana tertulis `instruction` sistem secara spesifik untuk memisahkan niat (*intent*) pengguna. 
Ketika Anda menjalankan `python adk_agent.py`, jika Anda bertanya "Ada tas ransel?", *agent* akan otomatis menggunakan `product_recommendation_tool`. Sebaliknya, jika ditanya "Bagaimana cara refund?", *agent* akan menggunakan `common_information_tool`.

---

## 🚀 Cara Menjalankan Project

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Jalankan Storing ke MongoDB:**
   ```bash
   python store_to_mongodb.py
   ```
   *(Pastikan Connection String di file tersebut menggunakan username dan password Anda yang tepat)*
3. **Mulai Chatting dengan Agent:**
   ```bash
   python adk_agent.py
   ```
   Lalu cobalah tanyakan pertanyaan tentang barang dan pertanyaan tentang kebijakan toko untuk melihat proses *routing* ADK berjalan.
