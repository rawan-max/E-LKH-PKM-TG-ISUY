import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-LKH Puskesmas Tanjung Isuy", layout="centered")

# Kamus Bahasa Indonesia
HARI_ID = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
BULAN_ID = {1: "JANUARI", 2: "FEBRUARI", 3: "MARET", 4: "APRIL", 5: "MEI", 6: "JUNI", 7: "JULI", 8: "AGUSTUS", 9: "SEPTEMBER", 10: "OKTOBER", 11: "NOVEMBER", 12: "DESEMBER"}

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
            st.session_state.master_data = df
            st.rerun()
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")

# --- 2. LOGIKA LOGIN ---
if st.session_state.master_data is not None:
    df = st.session_state.master_data
    col_nama = next((c for c in df.columns if 'NAMA' in c), None)
    
    if 'user' not in st.session_state:
        st.subheader("🔐 Login Pegawai")
        list_nama = sorted(df[col_nama].dropna().unique())
        nama_pilih = st.selectbox("Pilih Nama:", ["-- Pilih --"] + list_nama)
        
        if st.button("Masuk"):
            if nama_pilih != "-- Pilih --":
                row = df[df[col_nama] == nama_pilih].iloc[0]
                
                # DETEKSI NIP / NIPPPK / NIPPPK PW (Hapus NRTKK)
                label_fix = "NIP"
                nilai_fix = "-"
                # Cari kolom yang mengandung 'NIP' tapi bukan 'NRTKK'
                for c in df.columns:
                    if "NIP" in c and "NRTKK" not in c:
                        val = str(row.get(c, "-")).split('.')[0].strip() # Menghilangkan .0 jika ada
                        if val not in ["nan", "-", "", "None"]:
                            label_fix = c
                            nilai_fix = val
                            break
                
                st.session_state.user = {
                    "nama": nama_pilih,
                    "label": label_fix,
                    "id": nilai_fix,
                    "jabatan": str(row.get('JABATAN', 'Pegawai')),
                    "atasan_nama": "dr. Irana Priska",
                    "atasan_nip": "19880929 201503 2 007"
                }
                st.rerun()
    else:
        # --- 3. INPUT AKTIVITAS ---
        u = st.session_state.user
        st.sidebar.success(f"Login: {u['nama']}")
        if st.sidebar.button("Log Out"):
            st.session_state.clear()
            st.rerun()

        with st.form("input_lkh", clear_on_submit=True):
            st.subheader("📝 Input Laporan")
            tgl = st.date_input("Tanggal")
            c1, c2 = st.columns(2)
            jam_m = c1.text_input("Mulai (Contoh: 07:45)", "07.45")
            jam_s = c2.text_input("Selesai (Contoh: 14.00)", "14.00")
            akt = st.text_area("Aktivitas Kerja")
            out = st.text_input("Output", "1 Kegiatan")
            
            if st.form_submit_button("Simpan Ke Tabel"):
                if 'list_lkh' not in st.session_state: st.session_state.list_lkh = []
                try:
                    # Toleransi input menggunakan titik (.) atau titik dua (:)
                    m_fix = jam_m.replace(".", ":")
                    s_fix = jam_s.replace(".", ":")
                    t1 = datetime.strptime(m_fix, "%H:%M")
                    t2 = datetime.strptime(s_fix, "%H:%M")
                    durasi = int((t2 - t1).total_seconds() / 60)
                    
                    st.session_state.list_lkh.append({
                        "hari": HARI_ID.get(tgl.strftime("%A"), tgl.strftime("%A")),
                        "tgl": tgl.strftime("%d"),
                        "bln": BULAN_ID.get(tgl.month),
                        "waktu": f"{jam_m} - {jam_s}",
                        "akt": akt, "out": out, "durasi": durasi
                    })
                    st.rerun()
                except:
                    st.error("Format jam salah! Gunakan HH.MM (Contoh: 07.45)")

        # --- 4. TAMPILAN LAPORAN ---
        if 'list_lkh' in st.session_state and len(st.session_state.list_lkh) > 0:
            st.write("---")
            latest = st.session_state.list_lkh[-1]
            total_menit = sum(i['durasi'] for i in st.session_state.list_lkh)

            baris_html = ""
            for idx, item in enumerate(st.session_state.list_lkh):
                baris_html += f"<tr><td>{idx+1}</td><td>{item['waktu']}</td><td style='text-align:left;'>{item['akt']}</td><td>{item['out']}</td><td>{item['durasi']}</td></tr>"

            html_final = f"""
            <div style="background:white; color:black; padding:25px; font-family:Arial; border:1px solid #ddd;">
                <h3 style="text-align:center; text-decoration:underline;">LAPORAN KERJA HARIAN</h3>
                <table style="width:100%; font-size:13px; border:none; margin-bottom:15px;">
                    <tr><td width="130">BULAN</td><td>: {latest['bln']}</td></tr>
                    <tr><td>HARI</td><td>: {latest['hari']}</td></tr>
                    <tr><td>TANGGAL</td><td>: {latest['tgl']}</td></tr>
                    <tr><td>NAMA</td><td>: {u['nama']}</td></tr>
                    <tr><td>{u['label']}</td><td>: {u['id']}</td></tr>
                    <tr><td>JABATAN</td><td>: {u['jabatan']}</td></tr>
                    <tr><td>UNIT KERJA</td><td>: UPTD Puskesmas Tanjung Isuy</td></tr>
                </table>
                <table border="1" style="width:100%; border-collapse:collapse; text-align:center; font-size:12px;">
                    <tr style="background:#f2f2f2;"><th>NO</th><th>WAKTU</th><th>AKTIVITAS</th><th>OUTPUT</th><th>DURASI (MENIT)</th></tr>
                    {baris_html}
                    <tr style="font-weight:bold;"><td colspan="4" style="text-align:right; padding-right:10px;">JUMLAH</td><td>{total_menit}</td></tr>
                </table>
                <div style="margin-top:50px; display:flex; justify-content:space-between; font-size:13px; text-align:center;">
                    <div style="width:45%;">Menyetujui<br>Atasan Langsung<br><br><br><br><br><b><u>{u['atasan_nama']}</u></b><br>NIP. {u['atasan_nip']}</div>
                    <div style="width:45%;">{u['jabatan']}<br>UPTD Puskesmas Tanjung Isuy<br><br><br><br><br><b><u>{u['nama']}</u></b><br>{u['label']}. {u['id']}</div>
                </div>
            </div>
            """
            st.components.v1.html(html_final, height=600, scrolling=True)
            st.info("💡 Tekan Ctrl+P untuk mencetak ke PDF.")
