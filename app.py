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
        df = pd.read_excel(file)
        df.columns = [str(c).upper().strip() for c in df.columns]
        st.session_state.master_data = df
        st.rerun()
    st.stop()

df = st.session_sta_
