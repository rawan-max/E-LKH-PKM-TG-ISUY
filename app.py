import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# Kamus Konversi Bahasa Indonesia
HARI_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}
BULAN_ID = {
    1: "JANUARI", 2: "FEBRUARI", 3: "MARET", 4: "APRIL", 5: "MEI", 6: "JUNI",
    7: "JULI", 8: "AGUSTUS", 9: "SEPTEMBER", 10: "OKTOBER", 11: "NOVEMBER", 12: "DESEMBER"
}

# --- 1. PROSES MASTER DATA ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("🏥 E-LKH Mobile")
    file = st.file_uploader("Upload Master Data Pegawai (Excel)", type=['xlsx', 'xlsm'])
    if file:
        try:
            df = pd.read_excel(file, sheet_name=0)
            df.columns = [str(col).upper().strip() for col in df.columns]
