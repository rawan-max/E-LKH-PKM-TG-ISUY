import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# --- 1. DATA PEGAWAI ---
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

# --- 2. LOGIN ---
if st.session_state.master_data is not None:
    df = st.session_state.master_data
    col_nama = next((c for c in df.columns if 'NAMA' in c), "NAMA")
    
    if 'user' not in st.session_state:
        st.subheader("🔐 Login")
        nama_pilih = st.selectbox("Pilih Nama:", ["-- Pilih --"] + sorted(df[col_nama].dropna().unique()))
        if st.button("Masuk"):
            if nama_pilih != "-- Pilih --":
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
        st.sidebar.info(f"Pegawai: {u['nama']}")
        if st.sidebar.button("Keluar"):
            st.session_state.clear()
            st.rerun()

        # --- 3. INPUT FORM ---
        with st.form("form_lkh", clear_on_submit=True):
            st.subheader("📝 Input Aktivitas")
            tgl = st.date_input("Tanggal")
            c1, c2 = st.columns(2)
            jam_m = c1.text_input("Mulai", "07.45")
            jam_s = c2.text_input("Selesai", "14.00")
            akt = st.text_area("Aktivitas")
            out = st.text_input("Output", "1 Kegiatan")
            
            if st.form_submit_button("Simpan"):
                if 'list_lkh' not in st.session_state: st.session_state.list_lkh = []
                t1 = datetime.strptime(jam_m.replace(".", ":"), "%H:%M")
                t2 = datetime.strptime(jam_s.replace(".", ":"), "%H:%M")
                durasi = int((t2 - t1).total_seconds() / 60)
                
                st.session_state.list_lkh.append({
                    "hari": tgl.strftime("%A"), "tgl": tgl.strftime("%d"),
                    "bln": tgl.strftime("%B").upper(), "waktu": f"{jam_m} - {jam_s}",
                    "akt": akt, "out": out, "durasi": durasi
                })
                st.rerun()

        # --- 4. TAMPILAN LAPORAN ---
        if 'list_lkh' in st.session_state and len(st.session_state.list_lkh) > 0:
            st.divider()
            latest = st.session_state.list_lkh[-1]
            total = sum(i['durasi'] for i in st.session_state.list_lkh)

            baris = ""
            for idx, item in enumerate(st.session_state.list_lkh):
                baris += f"<tr><td>{idx+1}</td><td>{item['waktu']}</td><td style='text-align:left;'>{item['akt']}</td><td>{item['out']}</td><td>{item['durasi']}</td></tr>"

            # Gabungkan HTML dan CSS dalam satu string
            html_content = f"""
            <div style="background:white; color:black; padding:20px; font-family:Arial;">
                <h3 style="text-align:center; text-decoration:underline;">LAPORAN KERJA HARIAN</h3>
                <table style="width:100%; font-size:12px; border:none;">
                    <tr><td width="100">BULAN</td><td>: {latest['bln']}</td></tr>
                    <tr><td>HARI</td><td>: {latest['hari']}</td></tr>
                    <tr><td>TANGGAL</td><td>: {latest['tgl']}</td></tr>
                    <tr><td>NAMA</td><td>: {u['nama']}</td></tr>
                    <tr><td>NIP</td><td>: {u['nip']}</td></tr>
                    <tr><td>JABATAN</td><td>: {u['jabatan']}</td></tr>
                </table>
                <table border="1" style="width:100%; border-collapse:collapse; margin-top:10px; text-align:center; font-size:12px;">
                    <tr style="background:#eee;"><th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI</th></tr>
                    {baris}
                    <tr style="font-weight:bold;"><td colspan="4" style="text-align:right;">JUMLAH</td><td>{total}</td></tr>
                </table>
                <div style="margin-top:30px; display:flex; justify-content:space-between; font-size:12px; text-align:center;">
                    <div style="width:45%;">Menyetujui<br>Atasan Langsung<br><br><br><br><b><u>{u['atasan']}</u></b><br>NIP. {u['nip_atasan']}</div>
                    <div style="width:45%;">{u['jabatan']}<br>PKM Tanjung Isuy<br><br><br><br><b><u>{u['nama']}</u></b><br>NIP. {u['nip']}</div>
                </div>
            </div>
            """
            
            # MENGGUNAKAN COMPONENTS UNTUK RENDER PASTI
            st.components.v1.html(html_content, height=500, scrolling=True)
            st.button("🖨️ Cetak PDF (Gunakan Ctrl+P)")
