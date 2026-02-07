import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="E-LKH Mobile",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "data_lkh.csv"

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
    font-size: 16px !important;
    padding: 10px !important;
}
.stButton button {
    width: 100%;
    background-color: #FF4B4B;
    color: white;
    height: 55px;
    font-weight: bold;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# KAMUS
# =====================================================
HARI_ID = {
    "Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu",
    "Thursday":"Kamis","Friday":"Jumat",
    "Saturday":"Sabtu","Sunday":"Minggu"
}
BULAN_ID = {
    1:"JANUARI",2:"FEBRUARI",3:"MARET",4:"APRIL",5:"MEI",6:"JUNI",
    7:"JULI",8:"AGUSTUS",9:"SEPTEMBER",10:"OKTOBER",11:"NOVEMBER",12:"DESEMBER"
}

# =====================================================
# UTILITAS
# =====================================================
def parse_jam(jam_str):
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

# =====================================================
# UPLOAD MASTER DATA PEGAWAI
# =====================================================
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

df = st.session_state.master_data

# =====================================================
# DETEKSI KOLOM AMAN (FIX StopIteration)
# =====================================================
KEYWORDS_NAMA = ["NAMA", "NAME", "PEGAWAI"]
KEYWORDS_NIP  = ["NIP", "NIK", "NO"]

col_nama = next((c for c in df.columns i_
