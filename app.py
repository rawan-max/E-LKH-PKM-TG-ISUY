import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# CSS untuk desain laporan
STYLE_LAPORAN = """
<style>
    .laporan-container {
        background-color: white;
        padding: 40px;
        color: black;
        font-family: 'Arial', sans-serif;
        border: 1px solid #ddd;
    }
    .judul { text-align: center; font-weight: bold; text-decoration: underline; font-size: 18px; margin-bottom: 20px; }
    .tabel-meta { width: 100%; border: none; margin-bottom: 20px; font-size: 14px; }
    .tabel-data { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .tabel-data th, .tabel-data td { border: 1px solid black !important; padding: 8px; text-align: center; font-size: 13px; }
    .area-ttd { margin-top: 50px; display: flex; justify-content: space-between; }
    .box-ttd { text-align: center; width: 45%; font-size: 14px; }
</style>
"""

st.markdown(STYLE_LAPORAN, unsafe_allow_html=True)

# --- 2. LOGIKA DATABASE ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("🏥 E-LKH Mobile")
    file = st.file_uploader("Upload Master Data Pegawai", type=['xlsx', 'xlsm'])
    if file:
        df = pd.read_excel(file, sheet_name=0)
        df.columns = [str(col).upper().strip() for col in df.columns]
        st.session_state.master_data = df
        st.rerun()

# --- 3. LOGIN & INPUT ---
if st.session_state.master_data is not None:
    df = st.session_state.master_data
    col_nama = next((c for c in df.columns if 'NAMA' in c), "NAMA")
    
    if 'user' not in st.session_state:
        st.subheader("🔐 Login")
        nama_pilih = st.selectbox("Pilih Nama:", ["-- Pilih --"] + sorted(df[col_nama].dropna().unique()))
        if st.button("Masuk"):
            row = df[df[col_nama] == nama_pilih].iloc[0]
            st.session_state.user = {
                "nama": nama_pilih,
                "nip": str(row.get('NIP', '-')),
                "jabatan": str(row.get('JABATAN', '-')),
                "atasan": "dr. Irana Priska",
                "nip_atasan": "19880929 201503 2 007"
            }
            st.rerun()
    else:
        u = st.session_state.user
        st.sidebar.write(f"Login: **{u['nama']}**")
        if st.sidebar.button("Log Out"):
            st.session_state.clear()
            st.rerun()

        # FORM INPUT
        with st.form("input_lkh", clear_on_submit=True):
            st.subheader("📝 Tambah Aktivitas")
            tgl = st.date_input("Tanggal")
            c1, c2 = st.columns(2)
            m = c1.text_input("Mulai (07.45)", "07.45")
            s = c2.text_input("Selesai (14.00)", "14.00")
            akt = st.text_area("Aktivitas")
            out = st.text_input("Output", "1 Kegiatan")
            
            if st.form_submit_button("Simpan"):
                if 'list_lkh' not in st.session_state: st.session_state.list_lkh = []
                # Hitung Durasi
                t1 = datetime.strptime(m.replace(".", ":"), "%H:%M")
                t2 = datetime.strptime(s.replace(".", ":"), "%H:%M")
                durasi = int((t2 - t1).total_seconds() / 60)
                
                st.session_state.list_lkh.append({
                    "hari": tgl.strftime("%A"), "tgl": tgl.strftime("%d"),
                    "bln": tgl.strftime("%B").upper(), "waktu": f"{m} - {s}",
                    "akt": akt, "out": out, "durasi": durasi
                })

        # --- 4. RENDER TAMPILAN (CETAK) ---
        if 'list_lkh' in st.session_state and len(st.session_state.list_lkh) > 0:
            st.write("---")
            st.subheader("📄 Pratinjau Laporan")
            
            latest = st.session_state.list_lkh[-1]
            total = sum(item['durasi'] for item in st.session_state.list_lkh)

            # MEMBUAT STRING HTML
            baris_tabel = ""
            for i, item in enumerate(st.session_state.list_lkh):
                baris_tabel += f"""
                <tr>
                    <td>{i+1}</td><td>{item['waktu']}</td><td style='text-align:left;'>{item['akt']}</td>
                    <td>{item['out']}</td><td>{item['durasi']}</td>
                </tr>"""

            html_final = f"""
            <div class="laporan-container">
                <div class="judul">LAPORAN KERJA HARIAN</div>
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
                        <tr><th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI (MENIT)</th></tr>
                    </thead>
                    <tbody>
                        {baris_tabel}
                        <tr style="font-weight:bold;"><td colspan="4" style="text-align:right;">JUMLAH</td><td>{total}</td></tr>
                    </tbody>
                </table>
                <div class="area-ttd">
                    <div class="box-ttd">
                        Menyetujui<br>Pejabat Penilai/ Atasan Langsung<br><br><br><br><br>
                        <b><u>{u['atasan']}</u></b><br>NIP. {u['nip_atasan']}
                    </div>
                    <div class="box-ttd">
                        {u['jabatan']}<br>UPTD Puskesmas Tanjung Isuy<br><br><br><br><br>
                        <b><u>{u['nama']}</u></b><br>NIP. {u['nip']}
                    </div>
                </div>
            </div>
            """
            
            # PERINTAH WAJIB AGAR KODE TIDAK MUNCUL SEBAGAI TEKS
            st.markdown(html_final, unsafe_allow_html=True)
            
            st.info("💡 Tekan Ctrl+P untuk menyimpan sebagai PDF")
