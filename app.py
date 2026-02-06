import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# CSS untuk tampilan cetak agar rapi
st.markdown("""
    <style>
    .print-container { background-color: white; padding: 40px; color: black; font-family: 'Arial'; border: 1px solid #ddd; }
    .doc-header { text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 20px; text-decoration: underline; }
    .meta-table { width: 100%; margin-bottom: 20px; }
    .meta-table td { padding: 2px 5px; vertical-align: top; }
    .signature-container { margin-top: 40px; display: flex; justify-content: space-between; }
    .sig-box { text-align: center; width: 45%; line-height: 1.2; }
    @media print { .no-print { display: none !important; } .print-container { border: none; padding: 0; } }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 E-LKH Mobile")

# --- 1. LOAD MASTER DATA ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    uploaded_file = st.file_uploader("Langkah 1: Upload Master Data Pegawai (.xlsm/.xlsx)", type=['xlsx', 'xlsm'])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df.columns = [str(col).upper().strip() for col in df.columns]
        st.session_state.master_data = df
        st.rerun()

# --- 2. LOGIN & SETUP ATASAN (SEKALI SAJA) ---
if st.session_state.master_data is not None and 'user_login' not in st.session_state:
    df = st.session_state.master_data
    # Deteksi kolom nama
    col_nama = next((c for c in df.columns if 'NAMA' in c), None)
    daftar_nama = sorted(df[col_nama].dropna().unique())
    
    with st.container(border=True):
        st.subheader("🔐 Login & Konfigurasi")
        
        # Pilih Nama Pegawai
        nama_user = st.selectbox("Pilih Nama Anda:", ["-- Pilih Nama --"] + daftar_nama)
        
        st.divider()
        st.write("🔍 **Pilih Atasan Langsung**")
        st.caption("Pilih atasan Anda dari daftar di bawah agar tidak perlu mengetik lagi.")
        
        # Pilih Nama Atasan dari Master Data yang sama
        nama_atasan_opt = st.selectbox("Pilih Nama Atasan:", ["-- Pilih Atasan --"] + daftar_nama)
        
        if st.button("Masuk & Simpan Profil"):
            if nama_user != "-- Pilih Nama --" and nama_atasan_opt != "-- Pilih Atasan --":
                # Ambil data Pegawai
                u_row = df[df[col_nama] == nama_user].iloc[0]
                # Ambil data Atasan
                a_row = df[df[col_nama] == nama_atasan_opt].iloc[0]
                
                st.session_state.user_login = {
                    "Nama": nama_user,
                    "NIP": u_row.get('NIP', u_row.get('NIP BARU', '-')),
                    "Jabatan": u_row.get('JABATAN', '-'),
                    "Unit": "UPTD Puskesmas Tanjung Isuy",
                    "Atasan_Nama": nama_atasan_opt,
                    "Atasan_NIP": a_row.get('NIP', a_row.get('NIP BARU', '-'))
                }
                st.success("Profil tersimpan!")
                st.rerun()
            else:
                st.error("Mohon pilih Nama Anda dan Nama Atasan!")

# --- 3. INPUT AKTIVITAS ---
if 'user_login' in st.session_state:
    user = st.session_state.user_login
    
    # Sidebar Info
    with st.sidebar:
        st.info(f"Pegawai: **{user['Nama']}**\n\nAtasan: **{user['Atasan_Nama']}**")
        if st.button("Log Out / Ganti Atasan"):
            del st.session_state.user_login
            st.rerun()

    with st.form("input_form", clear_on_submit=True):
        st.subheader("📝 Input Aktivitas")
        tgl = st.date_input("Tanggal", datetime.now())
        c1, c2 = st.columns(2)
        wkt_mulai = c1.text_input("Mulai (Contoh: 07.45)", "07.45")
        wkt_selesai = c2.text_input("Selesai (Contoh: 14.00)", "14.00")
        aktivitas = st.text_area("Deskripsi Aktivitas")
        output = st.text_input("Output (Contoh: 1 Kegiatan)")
        
        if st.form_submit_button("Simpan ke Laporan"):
            try:
                t1 = datetime.strptime(wkt_mulai.replace(".", ":"), "%H:%M")
                t2 = datetime.strptime(wkt_selesai.replace(".", ":"), "%H:%M")
                durasi = int((t2 - t1).total_seconds() / 60)
                
                if 'entries' not in st.session_state: st.session_state.entries = []
                st.session_state.entries.append({
                    "HARI": tgl.strftime("%A"), # Nanti bisa di-translate ke Indo
                    "TANGGAL": tgl.strftime("%d"),
                    "BULAN": tgl.strftime("%B").upper(),
                    "WAKTU": f"{wkt_mulai} - {wkt_selesai}",
                    "AKTIVITAS": aktivitas,
                    "OUTPUT": output,
                    "DURASI": durasi
                })
                st.toast("Data Berhasil Ditambahkan!")
            except:
                st.error("Format waktu salah (Gunakan HH.MM)")

    #
