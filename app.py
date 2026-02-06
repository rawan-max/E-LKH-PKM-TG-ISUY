import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# Kamus Hari Indonesia
HARI_INDO = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}

# CSS untuk tampilan cetak agar persis seperti PDF
st.markdown("""
    <style>
    .print-container { background-color: white; padding: 30px; color: black; font-family: 'Arial'; border: 1px solid #eee; line-height: 1.4; }
    .doc-header { text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 20px; text-decoration: underline; }
    .meta-table { width: 100%; margin-bottom: 15px; font-size: 14px; }
    .meta-table td { padding: 1px 5px; vertical-align: top; }
    .signature-container { margin-top: 30px; display: flex; justify-content: space-between; font-size: 14px; }
    .sig-box { text-align: center; width: 45%; }
    th { background-color: #f2f2f2; font-size: 13px; padding: 5px; }
    td { font-size: 13px; padding: 5px; }
    @media print { .no-print { display: none !important; } .print-container { border: none; padding: 0; } }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 E-LKH Mobile")

# --- 1. LOAD MASTER DATA ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.info("Silakan upload Master Data Pegawai untuk memulai.")
    uploaded_file = st.file_uploader("Upload File Excel", type=['xlsx', 'xlsm'])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df.columns = [str(col).upper().strip() for col in df.columns]
        st.session_state.master_data = df
        st.rerun()

# --- 2. LOGIN (HANYA PILIH NAMA PENGGUNA) ---
if st.session_state.master_data is not None and 'user_login' not in st.session_state:
    df = st.session_state.master_data
    col_nama = next((c for c in df.columns if 'NAMA' in c), None)
    daftar_nama = sorted(df[col_nama].dropna().unique())
    
    with st.container(border=True):
        st.subheader("🔐 Login Pegawai")
        u_nama = st.selectbox("Pilih Nama Anda:", ["-- Pilih Nama --"] + daftar_nama)
        
        if st.button("Masuk"):
            if u_nama != "-- Pilih Nama --":
                u_row = df[df[col_nama] == u_nama].iloc[0]
                
                # DATA ATASAN DIKUNCI SESUAI PERMINTAAN
                st.session_state.user_login = {
                    "Nama": u_nama,
                    "NIP": str(u_row.get('NIP', u_row.get('NIP BARU', '-'))),
                    "Jabatan": str(u_row.get('JABATAN', '-')),
                    "Unit": "UPTD Puskesmas Tanjung Isuy",
                    "Atasan_Nama": "dr. Irana Priska",
                    "Atasan_NIP": "19880929 201503 2 007"
                }
                st.rerun()
            else:
                st.error("Pilih nama Anda terlebih dahulu!")

# --- 3. INPUT AKTIVITAS ---
if 'user_login' in st.session_state:
    user = st.session_state.user_login
    
    with st.sidebar:
        st.header("👤 Profil Login")
        st.write(f"Nama: **{user['Nama']}**")
        st.write(f"NIP: **{user['NIP']}**")
        st.divider()
        if st.button("Log Out / Reset"):
            st.session_state.clear()
            st.rerun()

    with st.form("lkh_form", clear_on_submit=True):
        st.subheader("📝 Input Laporan")
        tgl = st.date_input("Tanggal", datetime.now())
        c1, c2 = st.columns(2)
        w_mulai = c1.text_input("Mulai (Contoh 07.45)", "07.45")
        w_selesai = c2.text_input("Selesai (Contoh 14.00)", "14.00")
        aktivitas = st.text_area("Deskripsi Aktivitas Kerja")
        output = st.text_input("Output (Contoh: 1 Kegiatan)")
        
        if st.form_submit_button("Simpan Aktivitas"):
            try:
                t1 = datetime.strptime(w_mulai.replace(".", ":"), "%H:%M")
                t2 = datetime.strptime(w_selesai.replace(".", ":"), "%H:%M")
                durasi = int((t2 - t1).total_seconds() / 60)
                
                if 'entries' not in st.session_state: st.session_state.entries = []
                
                st.session_state.entries.append({
                    "HARI": HARI_INDO.get(tgl.strftime("%A"), tgl.strftime("%A")),
                    "TANGGAL": tgl.strftime("%d"),
                    "BULAN": tgl.strftime("%B").upper(),
                    "WAKTU": f"{w_mulai} - {w_selesai}",
                    "AKTIVITAS": aktivitas,
                    "OUTPUT": output,
                    "DURASI": durasi
                })
                st.toast("✅ Berhasil ditambahkan!")
            except:
                st.error("Format waktu salah! Gunakan HH.MM (Contoh: 07.45)")

    # --- 4. TAMPILAN PRATINJAU / CETAK ---
    if 'entries' in st.session_state and len(st.session_state.entries) > 0:
        st.divider()
        st.subheader("📄 Pratinjau Dokumen")
        
        df_view = pd.DataFrame(st.session_state.entries)
        latest = st.session_state.entries[-1]
        
        html_doc = f"""
        <div class="print-container">
            <div class="doc-header">LAPORAN KERJA HARIAN</div>
            <table class="meta-table">
                <tr><td width="120">BULAN</td><td>: {latest['BULAN']}</td></tr>
                <tr><td>HARI</td><td>: {latest['HARI']}</td></tr>
                <tr><td>TANGGAL</td><td>: {latest['TANGGAL']}</td></tr>
                <tr><td>NAMA</td><td>: {user['Nama']}</td></tr>
                <tr><td>NIP</td><td>: {user['NIP']}</td></tr>
                <tr><td>JABATAN</td><td>: {user['Jabatan']}</td></tr>
                <tr><td>UNIT KERJA</td><td>: {user['Unit']}</td></tr>
            </table>
            <table border="1" style="width:100%; border-collapse: collapse; text-align:center;">
                <tr>
                    <th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI AKTIVITAS<br>(MENIT)</th>
                </tr>
        """
        for i, row in enumerate(st.session_state.entries):
            html_doc += f"<tr><td>{i+1}</td><td>{row['WAKTU']}</td><td style='text-align:left;'>{row['AKTIVITAS']}</td><td>{row['OUTPUT']}</td><td>{row['DURASI']}</td></tr>"
        
        html_doc += f"""
                <tr style="font-weight:bold;">
                    <td colspan="4" style="text-align:right;">JUMLAH</td><td>{df_view['DURASI'].sum()}</td>
                </tr>
            </table>
            
            <div class="signature-container">
                <div class="sig-box">
                    Menyetujui<br>Pejabat Penilai/ Atasan Langsung<br><br><br><br><br>
                    <b><u>{user['Atasan_Nama']}</u></b><br>NIP. {user['Atasan_NIP']}
                </div>
                <div class="sig-box">
                    {user['Jabatan']}<br>UPTD Puskesmas Tanjung Isuy<br><br><br><br><br>
                    <b><u>{user['Nama']}</u></b><br>NIP. {user['NIP']}
                </div>
            </div>
        </div>
        """
        st.markdown(html_doc, unsafe_allow_html=True)
        
        # Tombol download csv sebagai cadangan
        st.download_button("📥 Download Data (CSV)", df_view.to_csv(index=False), "LKH_Rekap.csv")
