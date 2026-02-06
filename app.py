import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="mobile")

# --- JUDUL & HEADER ---
st.title("🏥 E-LKH Mobile")
st.write("Aplikasi Input Laporan Kerja Harian")
st.divider()

# --- 1. UPLOAD DATABASE PEGAWAI (MASTER DATA) ---
# Di aplikasi nyata, file ini disimpan di server. 
# Untuk demo ini, user mengupload file Master Data-nya dulu.
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.info("Langkah 1: Upload File 'MASTER DATA KEPEGAWAIAN' Anda")
    uploaded_file = st.file_uploader("Upload Excel Master Data (.xlsx/.xlsm)", type=['xlsx', 'xlsm'])
    
    if uploaded_file:
        try:
            # Membaca Excel. Asumsi kolom di Excel memiliki header seperti: 
            # 'NAMA', 'NIP', 'JABATAN', 'EMAIL'
            # Jika header beda, kode akan menyesuaikan (default fallback).
            df_master = pd.read_excel(uploaded_file)
            
            # Normalisasi nama kolom agar huruf besar semua
            df_master.columns = [str(col).upper().strip() for col in df_master.columns]
            
            st.session_state.master_data = df_master
            st.success("Database Pegawai Berhasil Dimuat!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal membaca file Excel: {e}")
            st.stop()

# --- 2. LOGIN (Google/Proton Simulation) ---
if st.session_state.master_data is not None:
    if 'user_login' not in st.session_state:
        st.subheader("🔐 Login Pegawai")
        email_input = st.text_input("Masukkan Email Anda (Google/Proton)")
        
        if st.button("Masuk"):
            # Cek apakah kolom EMAIL ada di Excel Master Data
            df = st.session_state.master_data
            
            # (Untuk demo: Jika kolom EMAIL tidak ada di Excel, kita pakai pencarian Nama saja atau login bebas)
            if 'EMAIL' in df.columns:
                user_match = df[df['EMAIL'] == email_input]
            else:
                # Fallback: Jika Excel belum ada kolom email, kita simulasikan login berhasil
                # dan minta user memilih nama mereka dari daftar.
                st.warning("⚠️ Kolom 'EMAIL' tidak ditemukan di Excel Master Data. Silakan pilih nama manual untuk demo.")
                user_match = pd.DataFrame() # Kosong

            if not user_match.empty:
                # Login Berhasil via Email
                user_data = user_match.iloc[0]
                st.session_state.user_login = {
                    "Nama": user_data.get('NAMA', 'User'),
                    "NIP": user_data.get('NIP', '-'),
                    "Jabatan": user_data.get('JABATAN', '-'),
                    "Unit": "UPTD Puskesmas Tanjung Isuy" # Default sesuai PDF
                }
                st.rerun()
            else:
                # Mode Manual (Jika Excel belum rapi)
                st.session_state.temp_email = email_input
                st.session_state.show_name_picker = True

        # Jika login email gagal/kolom tidak ada, munculkan dropdown nama dari Excel
        if st.session_state.get('show_name_picker'):
            st.write("---")
            st.write("Pilih data pegawai Anda dari Master Data:")
            # Ambil daftar nama dari kolom yang mengandung kata 'NAMA'
            col_nama = next((c for c in st.session_state.master_data.columns if 'NAMA' in c), None)
            
            if col_nama:
                pilihan_nama = st.selectbox("Pilih Nama", st.session_state.master_data[col_nama].unique())
                if st.button("Konfirmasi Masuk"):
                    user_data = st.session_state.master_data[st.session_state.master_data[col_nama] == pilihan_nama].iloc[0]
                    st.session_state.user_login = {
                        "Nama": user_data.get(col_nama),
                        "NIP": user_data.get('NIP', user_data.get('NIP BARU', '-')), # Coba cari kolom NIP
                        "Jabatan": user_data.get('JABATAN', '-'),
                        "Unit": "UPTD Puskesmas Tanjung Isuy"
                    }
                    st.rerun()
            else:
                st.error("Format Excel tidak dikenali. Pastikan ada kolom 'NAMA'.")

# --- 3. FORM INPUT LKH (Setelah Login) ---
if 'user_login' in st.session_state:
    user = st.session_state.user_login
    
    # Header Profil Otomatis
    st.success(f"Login sebagai: **{user['Nama']}**")
    with st.expander("Lihat Detail Profil"):
        st.write(f"**NIP:** {user['NIP']}")
        st.write(f"**Jabatan:** {user['Jabatan']}")
        st.write(f"**Unit Kerja:** {user['Unit']}")

    st.divider()
    
    # Form Input
    st.subheader("📝 Input Kegiatan Baru")
    
    with st.form("form_lkh"):
        tanggal = st.date_input("Tanggal Kegiatan", datetime.now())
        
        c1, c2 = st.columns(2)
        waktu_mulai = c1.time_input("Jam Mulai", datetime.strptime("07:30", "%H:%M").time())
        waktu_selesai = c2.time_input("Jam Selesai", datetime.now().time())
        
        aktivitas = st.text_area("Aktivitas", placeholder="Contoh: Apel Pagi, Menginput Data BPJS...")
        output = st.text_input("Output/Hasil", placeholder="Contoh: 1 Kegiatan, 5 Dokumen")
        
        simpan = st.form_submit_button("Simpan Laporan", type="primary")
        
        if simpan:
            # Hitung Durasi (Menit)
            t1 = datetime.combine(tanggal, waktu_mulai)
            t2 = datetime.combine(tanggal, waktu_selesai)
            durasi_menit = int((t2 - t1).total_seconds() / 60)
            
            if durasi_menit <= 0:
                st.error("Waktu selesai harus lebih besar dari waktu mulai!")
            else:
                # Simpan ke Session State (Database Sementara)
                if 'db_lkh' not in st.session_state:
                    st.session_state.db_lkh = []
                
                entri_baru = {
                    "BULAN": tanggal.strftime("%B").upper(), # Contoh: DESEMBER
                    "HARI": tanggal.strftime("%A"),
                    "TANGGAL": tanggal.day,
                    "NAMA": user['Nama'],
                    "NIP": user['NIP'],
                    "JABATAN": user['Jabatan'],
                    "UNIT KERJA": user['Unit'],
                    "WAKTU": f"{waktu_mulai.strftime('%H.%M')} - {waktu_selesai.strftime('%H.%M')}",
                    "AKTIVITAS": aktivitas,
                    "OUTPUT": output,
                    "DURASI (MENIT)": durasi_menit
                }
                st.session_state.db_lkh.append(entri_baru)
                st.toast("✅ Data berhasil disimpan!")

    # --- 4. REKAPAN & DOWNLOAD ---
    st.divider()
    st.subheader("📂 Rekapan Laporan Anda")
    
    if 'db_lkh' in st.session_state and st.session_state.db_lkh:
        df_lkh = pd.DataFrame(st.session_state.db_lkh)
        
        # Tampilkan Tabel Sederhana
        st.dataframe(df_lkh[['TANGGAL', 'Waktu', 'Aktivitas', 'Output', 'DURASI (MENIT)']], use_container_width=True)
        
        # Hitung Total Durasi
        total_menit = df_lkh['DURASI (MENIT)'].sum()
        st.metric("Total Durasi Bulan Ini", f"{total_menit} Menit")
        
        # Tombol Download Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_lkh.to_excel(writer, index=False, sheet_name='LKH Bulanan')
            
        st.download_button(
            label="📥 Download Format Excel",
            data=buffer,
            file_name=f"LKH_{user['Nama']}_{datetime.now().strftime('%B')}.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        # Tombol Reset
        if st.button("Hapus Semua Data (Reset)"):
            st.session_state.db_lkh = []
            st.rerun()
    else:
        st.info("Belum ada data yang diinput hari ini.")
