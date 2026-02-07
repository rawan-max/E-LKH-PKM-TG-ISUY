import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------------------
# KONFIGURASI HALAMAN STREAMLIT
# ------------------------------
st.set_page_config(
    page_title="E-LKH Mobile",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "data_lkh.csv"

# Kamus hari & bulan Indonesia
HARI_ID = {
    "Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu",
    "Thursday":"Kamis","Friday":"Jumat",
    "Saturday":"Sabtu","Sunday":"Minggu"
}
BULAN_ID = {
    1:"JANUARI",2:"FEBRUARI",3:"MARET",4:"APRIL",5:"MEI",6:"JUNI",
    7:"JULI",8:"AGUSTUS",9:"SEPTEMBER",10:"OKTOBER",11:"NOVEMBER",12:"DESEMBER"
}

# ------------------------------
# FUNGSIONALITAS UTAMA
# ------------------------------
def parse_jam(jam_str):
    """Ubah format jam fleksibel menjadi datetime"""
    jam_str = jam_str.replace(".", ":").strip()
    if ":" not in jam_str:
        raise ValueError
    jam, menit = jam_str.split(":")
    return datetime.strptime(f"{jam.zfill(2)}:{menit.zfill(2)}", "%H:%M")

def save_data(data):
    pd.DataFrame(data).to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["obj_date"]).to_dict("records")
    return []

# ------------------------------
# 1. UPLOAD MASTER DATA PEGAWAI
# ------------------------------
if "master_data" not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("📂 Setup Data Pegawai")
    file = st.file_uploader("Upload Excel Pegawai", type=["xlsx"])
    if file:
        try:
            df = pd.read_excel(file)
            df.columns = [str(c).upper().strip() for c in df.columns]
            st.session_state.master_data = df
            st.rerun()
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
    st.stop()

# Pastikan master_data ada
df = st.session_state.master_data

# ------------------------------
# 2. LOGIN HANYA DENGAN NAMA
# ------------------------------
if "user" not in st.session_state:
    st.title("🔐 Login E-LKH")
    
    # Cari kolom nama
    col_nama = next((c for c in df.columns if "NAMA" in c.upper()), None)
    if col_nama is None:
        st.error("Kolom NAMA PEGAWAI tidak ditemukan di Excel")
        st.code("\n".join(df.columns))
        st.stop()

    nama_list = df[col_nama].dropna().astype(str).str.strip().unique()
    nama = st.selectbox("Pilih Nama Anda", ["-- Pilih --"] + sorted(nama_list))

    if st.button("Masuk") and nama != "-- Pilih --":
        row = df[df[col_nama].astype(str).str.strip() == nama].iloc[0]
        st.session_state.user = {
            "nama": nama,
            "jabatan": row.get("JABATAN", "Pegawai")
        }
        st.session_state.data_lkh = load_data()
        st.rerun()

    st.stop()  # hentikan sebelum dashboard

# ------------------------------
# 3. DASHBOARD
# ------------------------------
u = st.session_state.user

with st.sidebar:
    st.success(f"👤 {u['nama']}")
    menu = st.radio("Menu", ["📝 Input Harian", "📊 Rekap Bulanan"])
    if st.button("Keluar"):
        st.session_state.clear()
        st.rerun()

# ------------------------------
# 4. INPUT HARIAN
# ------------------------------
if menu == "📝 Input Harian":
    st.header("📝 Input Aktivitas")

    tgl = st.date_input("Tanggal", datetime.now())
    c1, c2 = st.columns(2)
    jam_mulai = c1.text_input("Jam Mulai", "08.00")
    jam_selesai = c2.text_input("Jam Selesai", "14.00")
    kegiatan = st.text_area("Uraian Kegiatan")
    output = st.text_input("Output / Hasil", "1 Kegiatan")

    if st.button("💾 Simpan"):
        try:
            t1 = parse_jam(jam_mulai)
            t2 = parse_jam(jam_selesai)

            if t2 <= t1:
                st.error("Jam selesai harus lebih besar dari jam mulai")
                st.stop()

            durasi = int((t2 - t1
