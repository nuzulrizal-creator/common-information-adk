import streamlit as st
import asyncio
from adk_agent import smartshopper_agent

# Konfigurasi Halaman Web
st.set_page_config(page_title="SmartShopper Assistant", page_icon="🛒")

st.title("🛒 SmartShopper AI Assistant")
st.markdown("Tanyakan ketersediaan produk, spesifikasi barang, atau kebijakan toko (seperti COD, pengiriman, retur).")

# Inisialisasi history chat di session state agar tidak hilang saat direfresh
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history chat di layar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Form input untuk user
if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    # Tampilkan pesan user ke layar
    st.chat_message("user").markdown(prompt)
    # Simpan ke history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tampilkan respons AI
    with st.chat_message("assistant"):
        with st.spinner("Berpikir..."):
            try:
                # Memanggil ADK Agent secara asynchronous
                response = asyncio.run(smartshopper_agent.run(prompt))
                st.markdown(response)
                # Simpan respons AI ke history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Oops, terjadi kesalahan: {str(e)}\n\n*(Apakah API Key Anda sudah benar?)*"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
