import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

st.title("🏥 E-LKH Mobile")
st.write("UPTD Puskesmas Tanjung Isuy")
st.divider()

# --- 1. PROSES DATABASE PEGAWAI ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.info("Silakan Upload File MASTER DATA KEPEGAWAIAN (XLSM/XLSX)")
    uploaded_file = st.file_uploader("Pilih File", type=['xlsx', 'xlsm'])
    
    if uploaded_file:
        try:
            # Membaca sheet pertama sebagai default
            df_master = pd.read_excel(uploaded_file, sheet_name=0)
            
            # Membersihkan nama kolom (Hapus spasi & jadikan Upper Case)
            df_master.columns = [str(col).upper().strip() for col in df_master.columns]
            
            # Mencari kolom yang mengandung kata kunci tertentu
            col_nama = next((c for c in df_master.columns if 'NAMA' in c), None)
            col_nip = next((c for c in df_master.columns if 'NIP' in c), None)
            col_jabatan = next((c for c in df_master.columns if 'JABATAN' in c), None)
            
            if col_nama:
                st.session_state.master_data = df_master
                st.session_state.cols = {'nama': col_nama, 'nip': col_nip, 'jabatan': col_jabatan}
                st.success("Database Pegawai Berhasil Dimuat!")
                st.rerun()
            else:
                st.error("Gagal menemukan kolom 'NAMA' di file tersebut. Pastikan header tabel ada di baris pertama.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- 2. LOGIN ---
if st.session_state.master_data is not None:
    if 'user_login' not in st.session_state:
        st.subheader("🔐 Login Pegawai")
        df = st.session_state.master_data
        c_nama = st.session_state.cols['nama']
        
        # Mengambil daftar nama unik untuk dropdown (menghindari error input manual)
        daftar_nama = sorted(df[c_nama].dropna().unique())
        pilihan_nama = st.selectbox("Cari dan Pilih Nama Anda:", ["-- Pilih Nama --"] + daftar_nama)
        
        email_input = st.text_input("Konfirmasi Email (Google/Proton)")

        if st.button("Masuk"):
            if pilihan_nama != "-- Pilih Nama --":
                user_row = df[df[c_nama] == pilihan_nama].iloc[0]
                
                # Mengambil data NIP dan Jabatan jika kolomnya ada
                nip_val = user_row.get(st.session_state.cols['nip'], "-")
                jab_val = user_row.get(st.session_state.cols['jabatan'], "-")
                
                st.session_state.user_login = {
                    "Nama": pilihan_nama,
                    "NIP": nip_val,
                    "Jabatan": jab_val,
                    "Email": email_input
                }
                st.rerun()
            else:
                st.warning("Pilih nama terlebih dahulu!")

# --- 3. FORM INPUT LKH ---
if 'user_login' in st.session_state:
    user = st.session_state.user_login
    st.success(f"Login: **{user['Nama']}**")
    
    if st.button("Log Out"):
        del st.session_state.user_login
        st.rerun()

    with st.form("input_lkh"):
        st.subheader("📝 Input Aktivitas")
        tgl = st.date_input("Tanggal", datetime.now())
        
        col_w1, col_w2 = st.columns(2)
        jam_mulai = col_w1.time_input("Mulai", datetime.strptime("07:45", "%H:%M").time())
        jam_selesai = col_w2.time_input("Selesai", datetime.strptime("14:00", "%H:%M").time())
        
        aktivitas = st.text_area("Aktivitas Kerja")
        output = st.text_input("Output (Contoh: 1 Kegiatan / 5 Berkas)")
        
        if st.form_submit_button("Simpan"):
            # Hitung durasi
            durasi = (datetime.combine(tgl, jam_selesai) - datetime.combine(tgl, jam_mulai)).total_seconds() / 60
            
            if 'db_lkh' not in st.session_state: st.session_state.db_lkh = []
            
            st.session_state.db_lkh.append({
                "TANGGAL": tgl.strftime("%d/%m/%Y"),
                "HARI": tgl.strftime("%A"),
                "WAKTU": f"{jam_mulai.strftime('%H.%M')} - {jam_selesai.strftime('%H.%M')}",
                "AKTIVITAS": aktivitas,
                "OUTPUT": output,
                "DURASI (MENIT)": int(durasi)
            })
            st.toast("Data Tersimpan!")

    # --- 4. REKAP & DOWNLOAD ---
    if 'db_lkh' in st.session_state and st.session_state.db_lkh:
        st.divider()
        df_hasil = pd.DataFrame(st.session_state.db_lkh)
        st.write("### Rekap Hari Ini")
        st.table(df_hasil)
        
        # Download Excel
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            df_hasil.to_excel(writer, index=False, sheet_name='LKH')
        
        st.download_button(
            label="📥 Download Rekap Excel",
            data=output_excel.getvalue(),
            file_name=f"LKH_{user['Nama']}.xlsx",
            mime="application/vnd.ms-excel"
        )
