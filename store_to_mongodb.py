import json
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# 1. Konfigurasi Koneksi ke MongoDB Atlas
# Ganti dengan Connection String (URI) dari cluster MongoDB Atlas Anda.
# Sangat disarankan menggunakan environment variable untuk keamanan.
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb+srv://nuzulrizalnr_db_user:password123.@cluster0.e8mptlb.mongodb.net/?appName=Cluster0")

# Nama Database dan Collection yang akan digunakan
DB_NAME = "smartshopper_db"
COLLECTION_NAME = "common_information"

def main():
    try:
        # Membuat koneksi client ke MongoDB Atlas
        print("Menghubungkan ke MongoDB Atlas...")
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        
        # Mengecek koneksi dengan perintah ping
        client.admin.command('ping')
        print("Koneksi ke MongoDB Atlas berhasil!")

        # Mengakses database dan collection
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # 2. Membaca dataset dari file JSON lokal
        file_path = "common_information.json"
        print(f"Membaca data dari {file_path}...")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 3. Menyimpan data ke MongoDB (Insert Many)
        # Menghapus data lama jika ingin melakukan reset/update data secara bersih (Opsional)
        collection.delete_many({})
        print("Data lama di collection berhasil dibersihkan.")

        # Memasukkan data baru
        if data:
            result = collection.insert_many(data)
            print(f"Berhasil menyimpan {len(result.inserted_ids)} dokumen ke dalam collection '{COLLECTION_NAME}'.")
        else:
            print("Dataset kosong. Tidak ada data yang disimpan.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
