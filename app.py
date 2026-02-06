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
                
                # LOGIKA MENCARI JENIS NIP (NIP / NIPPPK / NIPPPK PW)
                # Mencari kolom yang mengandung kata 'NIP'
                id_label = "NIP"
                id_value = "-"
                for col in df.columns:
                    if "NIP" in col:
                        val = str(row.get(col, "-"))
                        if val != "nan" and val != "-":
                            id_label = col # Akan mengambil label sesuai kolom (NIP/NIPPPK/NIPPPK PW)
                            id_value = val
                            break
                
                st.session_state.user = {
                    "nama": nama_pilih,
                    "id_label": id_label,
                    "id_value": id_value,
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
                try:
                    t1 = datetime.strptime(jam_m.replace(".", ":"), "%H:%M")
                    t2 = datetime.strptime(jam_s.replace(".", ":"), "%H:%M")
                    durasi = int((t2 - t1).total_seconds() / 60)
                    
                    st.session_state.list_lkh.append({
                        "hari": tgl.strftime("%A"), "tgl": tgl.strftime("%d"),
                        "bln": tgl.strftime("%B").upper(), "waktu": f"{jam_m} - {jam_s}",
                        "akt": akt, "out": out, "durasi": durasi
                    })
                    st.rerun()
                except:
                    st.error("Format jam salah!")

        # --- 4. TAMPILAN LAPORAN (HTML RENDER) ---
        if 'list_lkh' in st.session_state and len(st.session_state.list_lkh) > 0:
            st.divider()
            latest = st.session_state.list_lkh[-1]
            total = sum(i['durasi'] for i in st.session_state.list_lkh)

            baris = ""
            for idx, item in enumerate(st.session_state.list_lkh):
                baris += f"<tr><td>{idx+1}</td><td>{item['waktu']}</td><td style='text-align:left;'>{item['akt']}</td><td>{item['out']}</td><td>{item['durasi']}</td></tr>"

            html_content = f"""
            <div style="background:white; color:black; padding:30px; font-family:Arial; border:1px solid #eee;">
                <h3 style="text-align:center; text-decoration:underline; margin-bottom:20px;">LAPORAN KERJA HARIAN</h3>
                <table style="width:100%; font-size:13px; border:none; margin-bottom:15px;">
                    <tr><td width="120">BULAN</td><td>: {latest['bln']}</td></tr>
                    <tr><td>HARI</td><td>: {latest['hari']}</td></tr>
                    <tr><td>TANGGAL</td><td>: {latest['tgl']}</td></tr>
                    <tr><td>NAMA</td><td>: {u['nama']}</td></tr>
                    <tr><td>{u['id_label']}</td><td>: {u['id_value']}</td></tr>
                    <tr><td>JABATAN</td><td>: {u['jabatan']}</td></tr>
                    <tr><td>UNIT KERJA</td><td>: UPTD Puskesmas Tanjung Isuy</td></tr>
                </table>
                <table border="1" style="width:100%; border-collapse:collapse; text-align:center; font-size:12px;">
                    <tr style="background:#f2f2f2;"><th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI</th></tr>
                    {baris}
                    <tr style="
