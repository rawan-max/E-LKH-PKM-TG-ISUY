import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# CSS Khusus untuk Tampilan Dokumen agar mirip PDF asli
STYLE_CETAK = """
<style>
    .laporan-box {
        background-color: white;
        padding: 30px;
        color: black;
        font-family: 'Arial', sans-serif;
        line-height: 1.5;
    }
    .header-dok {
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        text-decoration: underline;
        margin-bottom: 20px;
    }
    .tabel-meta { width: 100%; margin-bottom: 20px; border: none; }
    .tabel-meta td { padding: 2px 0; font-size: 14px; border: none !important; }
    
    .tabel-data {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .tabel-data th, .tabel-data td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: center;
        font-size: 13px;
    }
    .tanda-tangan-area {
        margin-top: 50px;
        display: flex;
        justify-content: space-between;
    }
    .box-ttd {
        text-align: center;
        width: 45%;
        font-size: 14px;
    }
    @media print {
        .no-print { display: none !important; }
        .laporan-box { border: none; padding: 0; }
    }
</style>
"""

st.markdown(STYLE_CETAK, unsafe_allow_html=True)

# Kamus Hari
HARI_ID = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}

st.title("🏥 E-LKH Tanjung Isuy")

# --- 1. DATA PEGAWAI ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.info("Silakan unggah Master Data Pegawai.")
    file_excel = st.file_uploader("Upload Excel", type=['xlsx', 'xlsm'])
    if file_excel:
        df = pd.read_excel(file_excel, sheet_name=0)
        df.columns = [str(col).upper().strip() for col in df.columns]
        st.session_state.master_data = df
        st.rerun()

# --- 2. LOGIN ---
if st.session_state.master_data is not None and 'user' not in st.session_state:
    df = st.session_state.master_data
    col_nama = next((c for c in df.columns if 'NAMA' in c), None)
    list_nama = sorted(df[col_nama].dropna().unique())
    
    with st.form("login_form"):
        nama_pilih = st.selectbox("Pilih Nama Anda:", ["-- Pilih --"] + list_nama)
        if st.form_submit_button("Masuk"):
            if nama_pilih != "-- Pilih --":
                row = df[df[col_nama] == nama_pilih].iloc[0]
                st.session_state.user = {
                    "nama": nama_pilih,
                    "nip": str(row.get('NIP', row.get('NIP BARU', '-'))),
                    "jabatan": str(row.get('JABATAN', '-')),
                    "atasan_nama": "dr. Irana Priska",
                    "atasan_nip": "19880929 201503 2 007"
                }
                st.rerun()

# --- 3. INPUT ---
if 'user' in st.session_state:
    u = st.session_state.user
    
    with st.sidebar:
        st.success(f"User: {u['nama']}")
        if st.button("Log Out"):
            st.session_state.clear()
            st.rerun()

    with st.form("input_lkh", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        tgl = col_a.date_input("Tanggal", datetime.now())
        output_txt = col_b.text_input("Output (Misal: 1 Kegiatan)")
        
        col_c, col_d = st.columns(2)
        jam_m = col_c.text_input("Jam Mulai", "07.45")
        jam_s = col_d.text_input("Jam Selesai", "14.00")
        
        aksi = st.text_area("Aktivitas Kerja")
        
        if st.form_submit_button("Tambahkan"):
            try:
                t1 = datetime.strptime(jam_m.replace(".", ":"), "%H:%M")
                t2 = datetime.strptime(jam_s.replace(".", ":"), "%H:%M")
                menit = int((t2 - t1).total_seconds() / 60)
                
                if 'data_lkh' not in st.session_state: st.session_state.data_lkh = []
                st.session_state.data_lkh.append({
                    "hari": HARI_ID.get(tgl.strftime("%A"), tgl.strftime("%A")),
                    "tgl": tgl.strftime("%d"),
                    "bln": tgl.strftime("%B").upper(),
                    "waktu": f"{jam_m} - {jam_s}",
                    "aktivitas": aksi,
                    "output": output_txt,
                    "durasi": menit
                })
                st.toast("Data ditambah!")
            except:
                st.error("Format jam salah (Gunakan 07.45)")

    # --- 4. TAMPILAN DOKUMEN (FIXED RENDER) ---
    if 'data_lkh' in st.session_state and len(st.session_state.data_lkh) > 0:
        st.divider()
        latest = st.session_state.data_lkh[-1]
        df_rekap = pd.DataFrame(st.session_state.data_lkh)
        
        # MEMBANGUN STRUKTUR HTML
        html_laporan = f"""
        <div class="laporan-box">
            <div class="header-dok">LAPORAN KERJA HARIAN</div>
            
            <table class="tabel-meta">
                <tr><td width="120">BULAN</td><td>: {latest['bln']}</td></tr>
                <tr><td>HARI</td><td>: {latest['hari']}</td></tr>
                <tr><td>TANGGAL</td><td>: {latest['tgl']}</td></tr>
                <tr><td>NAMA</td><td>: {u['nama']}</td></tr>
                <tr><td>NIP</td><td>: {u['nip']}</td></tr>
                <tr><td>JABATAN</td><td>: {u['jabatan']}</td></tr>
                <tr><td>UNIT KERJA</td><td>: UPTD Puskesmas Tanjung Isuy</td></tr>
            </table>

            <table class="tabel-data">
                <thead>
                    <tr>
                        <th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI AKTIVITAS (MENIT)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for idx, item in enumerate(st.session_state.data_lkh):
            html_laporan += f"""
                <tr>
                    <td>{idx+1}</td><td>{item['waktu']}</td><td style="text-align:left;">{item['aktivitas']}</td>
                    <td>{item['output']}</td><td>{item['durasi']}</td>
                </tr>
            """
            
        html_laporan += f"""
                <tr style="font-weight:bold;">
                    <td colspan="4" style="text-align:right;">JUMLAH</td><td>{df_rekap['durasi'].sum()}</td>
                </tr>
                </tbody>
            </table>

            <div class="tanda-tangan-area">
                <div class="box-ttd">
                    Menyetujui<br>Pejabat Penilai/ Atasan Langsung<br><br><br><br><br>
                    <b><u>{u['atasan_nama']}</u></b><br>NIP. {u['atasan_nip']}
                </div>
                <div class="box-ttd">
                    {u['jabatan']}<br>UPTD Puskesmas Tanjung Isuy<br><br><br><br><br>
                    <b><u>{u['nama']}</u></b><br>NIP. {u['nip']}
                </div>
            </div>
        </div>
        """
        
        # BAGIAN INI YANG MEMASTIKAN HTML DI-RENDER JADI TAMPILAN
        st.write("---")
        st.markdown(html_laporan, unsafe_allow_html=True)
        
        # Tombol Cetak Browser
        if st.button("🖨️ Cetak ke PDF"):
            st.info("Gunakan kombinasi tombol Ctrl + P (Windows) atau Command + P (Mac) pada keyboard Anda untuk menyimpan sebagai PDF.")
