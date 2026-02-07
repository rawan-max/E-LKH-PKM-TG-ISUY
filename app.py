import streamlit as st
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN (MOBILE FRIENDLY) ---
st.set_page_config(page_title="E-LKH Mobile", layout="centered", initial_sidebar_state="collapsed")

# CSS KHUSUS TAMPILAN HP & CETAK
st.markdown("""
<style>
    /* Tampilan di HP agar font tidak kekecilan */
    .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
        font-size: 16px !important;
    }
    /* Tombol simpan lebih besar di HP */
    .stButton button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 50px;
        font-weight: bold;
    }
    /* Container laporan agar rapi di layar kecil */
    .report-container {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
        background: white;
        color: black;
        font-family: Arial, sans-serif;
    }
    
    /* Tabel Responsif untuk Cetak */
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid black; padding: 4px; font-size: 12px; }
    
    @media print {
        .no-print { display: none !important; }
        .report-container { border: none; padding: 0; }
        th, td { font-size: 11px; }
    }
</style>
""", unsafe_allow_html=True)

# KAMUS WAKTU INDONESIA
HARI_ID = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
BULAN_ID = {1: "OKTOBER", 2: "FEBRUARI", 3: "MARET", 4: "APRIL", 5: "MEI", 6: "JUNI", 7: "JULI", 8: "AGUSTUS", 9: "SEPTEMBER", 10: "OKTOBER", 11: "NOVEMBER", 12: "DESEMBER"} # Disesuaikan Oktober contoh

# --- FUNGSI BANTUAN ---
def format_jam_flexible(jam_str):
    """Membersihkan input jam agar menerima titik atau titik dua."""
    jam_clean = jam_str.replace(".", ":").strip()
    # Tambahkan 0 di depan jika formatnya 7:45 -> 07:45
    if len(jam_clean.split(":")[0]) == 1:
        jam_clean = "0" + jam_clean
    return jam_clean

# --- 1. UPLOAD DATA ---
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

# --- 2. LOGIN ---
df = st.session_state.master_data
col_nama = next((c for c in df.columns if 'NAMA' in c), None)

if 'user' not in st.session_state:
    st.title("🔐 Login E-LKH")
    nama_user = st.selectbox("Pilih Nama Anda:", ["-- Pilih --"] + sorted(df[col_nama].dropna().unique()))
    if st.button("Masuk Aplikasi") and nama_user != "-- Pilih --":
        row = df[df[col_nama] == nama_user].iloc[0]
        
        # Logika Pencarian NIP / NIPPPK yang lebih kuat
        lbl_id, val_id = "NIP", "-"
        for c in df.columns:
            # Cari kolom mengandung NIP tapi bukan NRTKK
            if "NIP" in c and "NRTKK" not in c:
                clean_val = str(row.get(c, "")).replace(".0", "").strip()
                if clean_val not in ["nan", "-", "", "None"]:
                    lbl_id = c  # Simpan nama kolom aslinya (misal NIPPPK)
                    val_id = clean_val
                    break
        
        st.session_state.user = {
            "nama": nama_user,
            "label_id": lbl_id,
            "no_id": val_id,
            "jabatan": str(row.get('JABATAN', 'Pegawai')),
            "unit": "UPTD Puskesmas Tanjung Isuy",
            "atasan": "dr. Irana Priska",
            "nip_atasan": "19880929 201503 2 007"
        }
        st.rerun()

# --- 3. DASHBOARD UTAMA ---
if 'user' in st.session_state:
    u = st.session_state.user
    
    # MENU NAVIGASI (SIDEBAR)
    with st.sidebar:
        st.header(f"👤 {u['nama']}")
        st.text(f"{u['label_id']}: {u['no_id']}")
        st.markdown("---")
        menu = st.radio("Pilih Mode:", ["📝 Input Harian", "📊 Rekap Bulanan"])
        st.markdown("---")
        if st.button("Keluar"):
            st.session_state.clear()
            st.rerun()

    # --- MODE 1: INPUT HARIAN ---
    if menu == "📝 Input Harian":
        st.subheader("📝 Input Aktivitas Harian")
        
        with st.container(border=True):
            tgl_input = st.date_input("Tanggal")
            c1, c2 = st.columns(2)
            jam_masuk = c1.text_input("Mulai", "07.45", help="Bisa pakai titik atau titik dua")
            jam_pulang = c2.text_input("Selesai", "14.00")
            aktivitas = st.text_area("Uraian Kegiatan")
            output_kerja = st.text_input("Output (Hasil)", "1 Kegiatan")
            
            if st.button("💾 Simpan Aktivitas"):
                try:
                    # Proses Jam (Anti Error)
                    j_m = format_jam_flexible(jam_masuk)
                    j_k = format_jam_flexible(jam_pulang)
                    
                    t_start = datetime.strptime(j_m, "%H:%M")
                    t_end = datetime.strptime(j_k, "%H:%M")
                    durasi_menit = int((t_end - t_start).total_seconds() / 60)
                    
                    if 'data_lkh' not in st.session_state: st.session_state.data_lkh = []
                    
                    # Simpan Data
                    st.session_state.data_lkh.append({
                        "obj_date": tgl_input, # Disimpan sebagai objek date untuk sorting
                        "hari": HARI_ID.get(tgl_input.strftime("%A"), "-"),
                        "tgl_str": tgl_input.strftime("%d-%m-%Y"),
                        "jam": f"{j_m} - {j_k}",
                        "ket": aktivitas,
                        "out": output_kerja,
                        "durasi": durasi_menit
                    })
                    st.toast("✅ Data berhasil disimpan!", icon="check")
                except ValueError:
                    st.error("❌ Format jam tidak dikenali. Coba gunakan format 07:30 atau 07.30")

        # Preview Tabel Harian
        if 'data_lkh' in st.session_state and st.session_state.data_lkh:
            st.divider()
            st.caption("Pratinjau Laporan Harian (Scroll ke kanan jika tabel terpotong)")
            
            # Siapkan HTML Harian
            rows_html = ""
            total_harian = 0
            # Filter hanya menampilkan tanggal yang dipilih (opsional, saat ini tampil semua untuk rekap)
            # Disini kita tampilkan semua sesi input
            sorted_data = sorted(st.session_state.data_lkh, key=lambda x: x['obj_date'])
            
            for idx, d in enumerate(sorted_data):
                rows_html += f"<tr><td style='text-align:center'>{idx+1}</td><td style='text-align:center'>{d['jam']}</td><td>{d['ket']}</td><td style='text-align:center'>{d['out']}</td><td style='text-align:center'>{d['durasi']}</td></tr>"
                total_harian += d['durasi']
            
            html_view = f"""
            <div class="report-container">
                <div style="text-align:center; font-weight:bold; text-decoration:underline; margin-bottom:10px;">LAPORAN KERJA HARIAN</div>
                <table style="border:none; width:100%; margin-bottom:10px;">
                    <tr><td style="border:none; width:25%;">NAMA</td><td style="border:none">: {u['nama']}</td></tr>
                    <tr><td style="border:none">{u['label_id']}</td><td style="border:none">: {u['no_id']}</td></tr>
                    <tr><td style="border:none">JABATAN</td><td style="border:none">: {u['jabatan']}</td></tr>
                </table>
                <table>
                    <tr style="background:#f0f0f0; text-align:center;">
                        <th width="5%">NO</th><th width="15%">WAKTU</th><th>URAIAN KEGIATAN</th><th width="15%">OUTPUT</th><th width="10%">DURASI (MNT)</th>
                    </tr>
                    {rows_html}
                    <tr><td colspan="4" style="text-align:right; font-weight:bold;">JUMLAH</td><td style="text-align:center; font-weight:bold;">{total_harian}</td></tr>
                </table>
                <br>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div style="width:45%">Menyetujui,<br>Atasan Langsung<br><br><br><br><b><u>{u['atasan']}</u></b><br>NIP. {u['nip_atasan']}</div>
                    <div style="width:45%"><br>Pejabat Pembuat<br><br><br><br><b><u>{u['nama']}</u></b><br>{u['label_id']}. {u['no_id']}</div>
                </div>
            </div>
            """
            st.components.v1.html(html_view, height=600, scrolling=True)

    # --- MODE 2: REKAP BULANAN ---
    elif menu == "📊 Rekap Bulanan":
        st.subheader("📊 Laporan Capaian Bulanan")
        
        if 'data_lkh' not in st.session_state or not st.session_state.data_lkh:
            st.info("Belum ada data aktivitas yang diinput. Silakan input di menu 'Input Harian' terlebih dahulu.")
        else:
            # 1. Olah Data (Grouping per tanggal)
            df_raw = pd.DataFrame(st.session_state.data_lkh)
            # Group by tanggal objek
            rekap = df_raw.groupby('obj_date').agg({'durasi': 'sum'}).reset_index()
            rekap = rekap.sort
