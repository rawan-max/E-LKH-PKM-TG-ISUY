import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

st.title("🏥 E-LKH Mobile (Permanen)")
st.write("Input Laporan Kerja Harian - Data tersimpan otomatis")
st.divider()

# --- 1. PROSES DATABASE PEGAWAI (MASTER DATA) ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.info("Langkah Awal: Upload Master Data Kepegawaian")
    uploaded_file = st.file_uploader("Upload Excel Master Data", type=['xlsx', 'xlsm'])
    if uploaded_file:
        try:
            df_master = pd.read_excel(uploaded_file, sheet_name=0)
            df_master.columns = [str(col).upper().strip() for col in df_master.columns]
            col_nama = next((c for c in df_master.columns if 'NAMA' in c), None)
            if col_nama:
                st.session_state.master_data = df_master
                st.session_state.col_nama = col_nama
                st.success("Database Pegawai Aktif!")
                st.rerun()
        except Exception as e:
            st.error(f"Error baca file: {e}")

# --- 2. LOGIN ---
if st.session_state.master_data is not None:
    if 'user_login' not in st.session_state:
        st.subheader("🔐 Login")
        daftar_nama = sorted(st.session_state.master_data[st.session_state.col_nama].dropna().unique())
        pilihan_nama = st.selectbox("Pilih Nama Anda:", ["-- Pilih --"] + daftar_nama)
        email = st.text_input("Email (Google/Proton)")

        if st.button("Masuk"):
            if pilihan_nama != "-- Pilih --":
                # Ambil NIP & Jabatan otomatis
                row = st.session_state.master_data[st.session_state.master_data[st.session_state.col_nama] == pilihan_nama].iloc[0]
                st.session_state.user_login = {
                    "Nama": pilihan_nama,
                    "NIP": row.get('NIP', row.get('NIP BARU', '-')),
                    "Jabatan": row.get('JABATAN', '-'),
                    "Email": email
                }
                st.rerun()
    else:
        # --- 3. FORM INPUT (WAKTU MANUAL) ---
        user = st.session_state.user_login
        st.success(f"User: **{user['Nama']}**")
        
        if st.button("Keluar / Ganti User"):
            del st.session_state.user_login
            st.rerun()

        with st.form("input_form"):
            st.subheader("📝 Input LKH")
            tgl = st.date_input("Tanggal", datetime.now())
            
            # INPUT WAKTU SECARA MANUAL (TEXT)
            c1, c2 = st.columns(2)
            wkt_mulai = c1.text_input("Waktu Mulai (Contoh: 07.45)", value="07.45")
            wkt_selesai = c2.text_input("Waktu Selesai (Contoh: 14.00)", value="14.00")
            
            aktivitas = st.text_area("Aktivitas")
            output = st.text_input("Output (Contoh: 1 Kegiatan)")
            
            submit = st.form_submit_button("Simpan Permanen")
            
            if submit:
                try:
                    # Hitung Durasi dari input manual HH.MM
                    t1 = datetime.strptime(wkt_mulai.replace(".", ":"), "%H:%M")
                    t2 = datetime.strptime(wkt_selesai.replace(".", ":"), "%H:%M")
                    durasi = int((t2 - t1).total_seconds() / 60)
                    
                    data_baru = {
                        "NAMA": user['Nama'],
                        "TANGGAL": tgl.strftime("%d/%m/%Y"),
                        "WAKTU": f"{wkt_mulai} - {wkt_selesai}",
                        "AKTIVITAS": aktivitas,
                        "OUTPUT": output,
                        "DURASI (MENIT)": durasi
                    }
                    
                    # Simpan ke daftar lokal (Session)
                    if 'db_permanen' not in st.session_state:
                        st.session_state.db_permanen = []
                    st.session_state.db_permanen.append(data_baru)
                    
                    st.success(f"Data tersimpan! Durasi: {durasi} menit.")
                except Exception as e:
                    st.error("Format waktu salah! Gunakan format HH.MM (contoh 07.45)")

        # --- 4. REKAP & DOWNLOAD ---
        if 'db_permanen' in st.session_state:
            df_rekap = pd.DataFrame(st.session_state.db_permanen)
            st.divider()
            st.subheader("📊 Rekap Laporan")
            st.dataframe(df_rekap)
            
            # Tombol Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_rekap.to_excel(writer, index=False)
            st.download_button("📥 Download Excel", buffer.getvalue(), "Rekap_LKH.xlsx", "application/vnd.ms-excel")
