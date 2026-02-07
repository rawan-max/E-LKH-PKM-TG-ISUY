import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN (MOBILE FRIENDLY) ---
st.set_page_config(page_title="E-LKH Mobile", layout="centered", initial_sidebar_state="collapsed")

# CSS KHUSUS
st.markdown("""
<style>
    .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
        font-size: 16px !important;
        padding: 10px !important;
    }
    .stButton button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 55px;
        font-weight: bold;
        border-radius: 8px;
    }
    .report-box {
        border: 1px solid #ccc;
        padding: 15px;
        background: white;
        color: black;
        font-family: Arial, sans-serif;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid black; padding: 5px; font-size: 12px; }
    
    @media print {
        .no-print { display: none !important; }
        .report-box { border: none; padding: 0; }
        th, td { font-size: 11px; }
    }
</style>
""", unsafe_allow_html=True)

# KAMUS WAKTU INDONESIA
HARI_ID = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
BULAN_ID = {1: "JANUARI", 2: "FEBRUARI", 3: "MARET", 4: "APRIL", 5: "MEI", 6: "JUNI", 7: "JULI", 8: "AGUSTUS", 9: "SEPTEMBER", 10: "OKTOBER", 11: "NOVEMBER", 12: "DESEMBER"}

# --- 2. UPLOAD DATA ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("📂 Setup Data Pegawai")
    uploaded_file = st.file_uploader("Upload File Excel Pegawai", type=['xlsx'])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).upper().strip() for c in df.columns]
            st.session_state.master_data = df
            st.rerun()
        except Exception as e:
            st.error(f"Error file: {e}")
    st.stop()

# --- 3. LOGIN & PERBAIKAN ERROR OTOMATIS ---
df = st.session_state.master_data
col_nama = next((c for c in df.columns if 'NAMA' in c), None)

if 'user' not in st.session_state:
    st.title("🔐 Login E-LKH")
    nama_user = st.selectbox("Pilih Nama Anda:", ["-- Pilih --"] + sorted(df[col_nama].dropna().unique()))
    
    if st.button("Masuk Aplikasi") and nama_user != "-- Pilih --":
        row = df[df[col_nama] == nama_user].iloc[0]
        
        # Logika Pencarian NIP
        lbl_id, val_id = "NIP", "-"
        for c in df.columns:
            if "NIP" in c and "NRTKK" not in c:
                clean_val = str(row.get(c, "")).replace(".0", "").strip()
                if clean_val not in ["nan", "-", "", "None"]:
                    lbl_id = c
                    val_id = clean_val
                    break
        
        st.session_state.user = {
            "nama": nama_user,
            "label_id": lbl_id,
            "no_id": val_id,
            "jabatan": str(row.get('JABATAN', 'Pegawai')),
            "atasan": "dr. Irana Priska",
            "nip_atasan": "19880929 201503 2 007"
        }
        st.rerun()

# --- 4. DASHBOARD UTAMA ---
if 'user' in st.session_state:
    if 'label_id' not in st.session_state.user:
        st.session_state.clear()
        st.rerun()
        
    u = st.session_state.user
    
    with st.sidebar:
        st.success(f"👤 {u['nama']}")
        st.caption(f"{u['label_id']}: {u['no_id']}")
        st.divider()
        menu = st.radio("Menu:", ["📝 Input Harian", "📊 Rekap Bulanan"])
        st.divider()
        if st.button("Keluar"):
            st.session_state.clear()
            st.rerun()

    # ==========================
    # MODE 1: INPUT HARIAN
    # ==========================
    if menu == "📝 Input Harian":
        st.header("📝 Input Aktivitas")
        
        with st.container():
            tgl_input = st.date_input("Tanggal", datetime.now())
            c1, c2 = st.columns(2)
            jam_masuk = c1.text_input("Jam Mulai", "08.00")
            jam_pulang = c2.text_input("Jam Selesai", "14.00")
            aktivitas = st.text_area("Uraian Kegiatan", height=100)
            output_kerja = st.text_input("Output / Hasil", "1 Kegiatan")
            
            st.write("") 
            if st.button("💾 SIMPAN KEGIATAN"):
                try:
                    # Logika Jam Fleksibel
                    j_m = jam_masuk.replace(".", ":").strip()
                    j_k = jam_pulang.replace(".", ":").strip()
                    
                    if len(j_m.split(":")[0]) == 1: j_m = "0" + j_m
                    if len(j_k.split(":")[0]) == 1: j_k = "0" + j_k

                    t_start = datetime.strptime(j_m, "%H:%M")
                    t_end = datetime.strptime(j_k, "%H:%M")
                    durasi_menit = int((t_end - t_start).total_seconds() / 60)
                    
                    if 'data_lkh' not in st.session_state: st.session_state.data_lkh = []
                    
                    st.session_state.data_lkh.append({
                        "obj_date": tgl_input,
                        "hari": HARI_ID.get(tgl_input.strftime("%A"), "-"),
                        "tgl_str": tgl_input.strftime("%d-%m-%Y"),
                        "tgl_full": tgl_input,
                        "jam": f"{j_m} - {j_k}",
                        "ket": aktivitas,
                        "out": output_kerja,
                        "durasi": durasi_menit
                    })
                    # PERBAIKAN DI SINI (MENGGUNAKAN EMOJI ASLI)
                    st.toast("Data tersimpan!", icon="✅")
                    st.rerun()
                except:
                    st.error("Format jam salah. Gunakan contoh: 08.00")

        # Tabel Preview Harian
        if 'data_lkh' in st.session_state and st.session_state.data_lkh:
            st.markdown("---")
            st.subheader("📄 Preview Laporan Harian")
            
            sorted_data = sorted(st.session_state.data_lkh, key=lambda x: x['obj_date'])
            latest = sorted_data[-1]
            bulan_ini = BULAN_ID.get(latest['obj_date'].month, "BULAN INI")
            
            rows_html = ""
            total_harian = 0
            for idx, d in enumerate(sorted_data):
                rows_html += f"<tr><td style='text-align:center'>{idx+1}</td><td style='text-align:center'>{d['jam']}</td><td>{d['ket']}</td><td style='text-align:center'>{d['out']}</td><td style='text-align:center'>{d['durasi']}</td></tr>"
                total_harian += d['durasi']

            html_harian = f"""
            <div class="report-box">
                <div style="text-align:center; font-weight:bold; text-decoration:underline; margin-bottom:15px;">LAPORAN KERJA HARIAN</div>
                <table style="border:none; width:100%; margin-bottom:10px;">
                    <tr><td style="border:none; width:100px;">BULAN</td><td style="border:none">: {bulan_ini}</td></tr>
                    <tr><td style="border:none">NAMA</td><td style="border:none">: {u['nama']}</td></tr>
                    <tr><td style="border:none">{u['label_id']}</td><td style="border:none">: {u['no_id']}</td></tr>
                    <tr><td style="border:none">JABATAN</td><td style="border:none">: {u['jabatan']}</td></tr>
                </table>
                <table>
                    <tr style="background:#eee; text-align:center;">
                        <th width="5%">NO</th><th width="15%">WAKTU</th><th>AKTIVITAS</th><th width="15%">OUTPUT</th><th width="10%">MNT</th>
                    </tr>
                    {rows_html}
                    <tr style="font-weight:bold;"><td colspan="4" style="text-align:right;">JUMLAH</td><td style="text-align:center;">{total_harian}</td></tr>
                </table>
                <br>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div style="width:45%">Menyetujui,<br>Atasan Langsung<br><br><br><br><b><u>{u['atasan']}</u></b><br>NIP. {u['nip_atasan']}</div>
                    <div style="width:45%"><br>Pejabat Pembuat<br><br><br><br><b><u>{u['nama']}</u></b><br>{u['label_id']}. {u['no_id']}</div>
                </div>
            </div>
            """
            st.components.v1.html(html_harian, height=600, scrolling=True)

    # ==========================
    # MODE 2: REKAP BULANAN
    # ==========================
    elif menu == "📊 Rekap Bulanan":
        st.header("📊 Rekapitulasi Bulanan")
        
        if 'data_lkh' not in st.session_state or not st.session_state.data_lkh:
            st.info("⚠️ Belum ada data. Silakan input kegiatan di menu 'Input Harian' dulu.")
        else:
            df_raw = pd.DataFrame(st.session_state.data_lkh)
            rekap = df_raw.groupby('obj_date').agg({'durasi': 'sum'}).reset_index().sort_values('obj_date')
            
            TARGET_HARIAN = 270 
            total_capaian = rekap['durasi'].sum()
            total_target = len(rekap) * TARGET_HARIAN
            persen = (total_capaian / total_target * 100) if total_target > 0 else 0
            
            bulan_laporan = BULAN_ID.get(rekap.iloc[0]['obj_date'].month, "BULAN INI")

            rows_bln = ""
            for idx, row in rekap.iterrows():
                tgl_str = row['obj_date'].strftime("%d %B %Y")
                hari_str = HARI_ID.get(row['obj_date'].strftime("%A"), "")
                display_tgl = f"{hari_str}<br>{tgl_str}"
                
                rows_bln += f"""
                <tr>
                    <td style="text-align:center">{idx+1}</td>
                    <td style="text-align:center">{display_tgl}</td>
                    <td style="text-align:center">{row['durasi']}</td>
                    <td style="text-align:center">{TARGET_HARIAN}</td>
                </tr>"""
            
            html_bulanan = f"""
            <div class="report-box">
                <div style="text-align:center; font-weight:bold; margin-bottom:20px;">CAPAIAN PRODUKTIVITAS KERJA BULANAN</div>
                <table style="border:none; width:100%; margin-bottom:15px;">
                    <tr><td style="border:none; width:100px;">NAMA</td><td style="border:none">: {u['nama']}</td></tr>
                    <tr><td style="border:none">{u['label_id']}</td><td style="border:none">: {u['no_id']}</td></tr>
                    <tr><td style="border:none">JABATAN</td><td style="border:none">: {u['jabatan']}</td></tr>
                    <tr><td style="border:none">UNIT KERJA</td><td style="border:none">: UPTD Puskesmas Tanjung Isuy</td></tr>
                    <tr><td style="border:none">BULAN</td><td style="border:none">: {bulan_laporan}</td></tr>
                </table>
                
                <table>
                    <tr style="background:#eee; text-align:center;">
                        <th>NO</th><th>HARI / TANGGAL</th><th>CAPAIAN (MNT)</th><th>TARGET (MNT)</th>
                    </tr>
                    {rows_bln}
                    <tr style="font-weight:bold; background:#eee;">
                        <td colspan="2" style="text-align:right;">TOTAL</td>
                        <td style="text-align:center;">{total_capaian}</td>
                        <td style="text-align:center;">{total_target}</td>
                    </tr>
                </table>
                
                <div style="margin-top:20px; font-weight:bold;">
                    CAPAIAN: {persen:.2f}% ({'SANGAT BAIK' if persen >= 100 else 'BAIK'})
                </div>
                
                <div style="margin-top:40px; display:flex; justify-content:space-between; text-align:center;">
                    <div style="width:45%">Menyetujui,<br>Pejabat Penilai<br><br><br><br><b><u>{u['atasan']}</u></b><br>NIP. {u['nip_atasan']}</div>
                    <div style="width:45%"><br>Pegawai Yang Dinilai<br><br><br><br><b><u>{u['nama']}</u></b><br>{u['label_id']}. {u['no_id']}</div>
                </div>
            </div>
            """
            st.components.v1.html(html_bulanan, height=700, scrolling=True)
            st.info("💡 Tips: Tekan Ctrl + P untuk simpan PDF")
