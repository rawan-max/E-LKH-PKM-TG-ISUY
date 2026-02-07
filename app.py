import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================================================
# KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="E-LKH Mobile",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "data_lkh.csv"

# =========================================================
# CSS
# =========================================================
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
}
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid black; padding: 5px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# KAMUS
# =========================================================
HARI_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat",
    "Saturday": "Sabtu", "Sunday": "Minggu"
}
BULAN_ID = {
    1:"JANUARI",2:"FEBRUARI",3:"MARET",4:"APRIL",5:"MEI",6:"JUNI",
    7:"JULI",8:"AGUSTUS",9:"SEPTEMBER",10:"OKTOBER",11:"NOVEMBER",12:"DESEMBER"
}

# =========================================================
# UTILITAS
# =========================================================
def parse_jam(jam_str):
    jam_str = jam_str.replace(".", ":").strip()
    jam, menit = jam_str.split(":")
    return datetime.strptime(f"{jam.zfill(2)}:{menit.zfill(2)}", "%H:%M")

def save_data(data):
    pd.DataFrame(data).to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["obj_date"]).to_dict("records")
    return []

# =========================================================
# UPLOAD MASTER DATA
# =========================================================
if "master_data" not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("📂 Setup Data Pegawai")
    file = st.file_uploader("Upload Excel Pegawai", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        df.columns = [c.upper().strip() for c in df.columns]
        st.session_state.master_data = df
        st.rerun()
    st.stop()

df = st.session_state.master_data
col_nama = next(c for c in df.columns if "NAMA" in c)

# =========================================================
# LOGIN
# =========================================================
if "user" not in st.session_state:
    st.title("🔐 Login E-LKH")
    nama = st.selectbox("Pilih Nama", ["-- Pilih --"] + sorted(df[col_nama].dropna()))
    if st.button("Masuk") and nama != "-- Pilih --":
        row = df[df[col_nama] == nama].iloc[0]
        nip = "-"
        for c in df.columns:
            if "NIP" in c:
                nip = str(row[c]).replace(".0", "")
                break

        st.session_state.user = {
            "nama": nama,
            "nip": nip,
            "jabatan": row.get("JABATAN", "Pegawai"),
            "atasan": "dr. Irana Priska",
            "nip_atasan": "19880929 201503 2 007"
        }
        st.session_state.data_lkh = load_data()
        st.rerun()

# =========================================================
# DASHBOARD
# =========================================================
u = st.session_state.user

with st.sidebar:
    st.success(u["nama"])
    menu = st.radio("Menu", ["📝 Input Harian", "📊 Rekap Bulanan"])
    if st.button("Keluar"):
        st.session_state.clear()
        st.rerun()

# =========================================================
# INPUT HARIAN
# =========================================================
if menu == "📝 Input Harian":
    st.header("📝 Input Aktivitas")

    tgl = st.date_input("Tanggal", datetime.now())
    c1, c2 = st.columns(2)
    jam_mulai = c1.text_input("Jam Mulai", "08.00")
    jam_selesai = c2.text_input("Jam Selesai", "14.00")
    kegiatan = st.text_area("Uraian Kegiatan")
    output = st.text_input("Output", "1 Kegiatan")

    if st.button("💾 Simpan"):
        try:
            t1 = parse_jam(jam_mulai)
            t2 = parse_jam(jam_selesai)
            if t2 <= t1:
                st.error("Jam selesai harus lebih besar")
                st.stop()

            durasi = int((t2 - t1).total_seconds() / 60)

            st.session_state.data_lkh.append({
                "obj_date": tgl,
                "hari": HARI_ID[tgl.strftime("%A")],
                "jam": f"{jam_mulai} - {jam_selesai}",
                "ket": kegiatan,
                "out": output,
                "durasi": durasi
            })
            save_data(st.session_state.data_lkh)
            st.toast("Tersimpan ✅")
            st.rerun()
        except:
            st.error("Format jam salah")

    # PREVIEW + HAPUS
    st.markdown("---")
    for i, d in enumerate(st.session_state.data_lkh):
        c1, c2 = st.columns([9, 1])
        c1.markdown(f"**{d['jam']}**  \n{d['ket']}  \n{d['durasi']} menit")
        if c2.button("🗑️", key=f"del{i}"):
            st.session_state.data_lkh.pop(i)
            save_data(st.session_state.data_lkh)
            st.rerun()

# =========================================================
# REKAP BULANAN
# =========================================================
else:
    st.header("📊 Rekap Bulanan")

    if not st.session_state.data_lkh:
        st.info("Belum ada data")
        st.stop()

    df_raw = pd.DataFrame(st.session_state.data_lkh)
    df_raw["obj_date"] = pd.to_datetime(df_raw["obj_date"])

    bulan = st.selectbox(
        "Pilih Bulan",
        sorted(df_raw["obj_date"].dt.month.unique()),
        format_func=lambda x: BULAN_ID[x]
    )

    df_bln = df_raw[df_raw["obj_date"].dt.month == bulan]
    rekap = df_bln.groupby("obj_date")["durasi"].sum().reset_index()

    TARGET = 270
    rekap["target"] = TARGET

    st.dataframe(rekap, use_container_width=True)

    total = rekap["durasi"].sum()
    persen = total / (len(rekap) * TARGET) * 100

    st.success(f"Total: {total} menit | Capaian: {persen:.2f}%")
