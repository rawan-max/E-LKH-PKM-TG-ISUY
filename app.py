import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile
import pdfkit

# =======================
# Page Config & CSS
# =======================
st.set_page_config(page_title="E-LKH Mobile", layout="centered")

st.markdown("""
<style>
.stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {font-size:16px !important; padding:10px !important;}
.stButton button {width:100%; background-color:#FF4B4B; color:white; height:55px; font-weight:bold; border-radius:8px;}
.report-box {border:1px solid #ccc; padding:15px; background:white; color:black; font-family:Arial, sans-serif;}
table {width:100%; border-collapse: collapse;}
th, td {border:1px solid black; padding:5px; font-size:12px;}
@media print {.no-print {display:none !important;} .report-box {border:none; padding:0;} th, td {font-size:11px;}}
</style>
""", unsafe_allow_html=True)

# =======================
# Kamus Hari & Bulan
# =======================
HARI_ID = {"Monday": "Senin","Tuesday": "Selasa","Wednesday": "Rabu",
           "Thursday": "Kamis","Friday": "Jumat","Saturday": "Sabtu","Sunday": "Minggu"}
BULAN_ID = {1: "JANUARI",2: "FEBRUARI",3: "MARET",4: "APRIL",
            5: "MEI",6: "JUNI",7: "JULI",8: "AGUSTUS",
            9: "SEPTEMBER",10: "OKTOBER",11: "NOVEMBER",12: "DESEMBER"}

# =======================
# Helper Functions
# =======================
def parse_jam(jam_str):
    jam_str = jam_str.replace(".", ":").strip()
    if len(jam_str.split(":")[0]) == 1:
        jam_str = "0" + jam_str
    return datetime.strptime(jam_str, "%H:%M")

def export_pdf(html_content, filename="lkh.pdf"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdfkit.from_string(html_content, tmpfile.name)
        tmpfile.flush()
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="⬇️ Simpan PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )

# =======================
# Upload Data Pegawai
# =======================
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

if st.session_state.master_data is None:
    st.title("📂 Setup Data Pegawai")
    uploaded_file = st.file_uploader("Upload File Excel Pegawai", type=['xlsx'])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).upper().strip() for c in df.columns]
            if not any("NAMA" in c for c in df.columns):
                st.error("Kolom NAMA PEGAWAI tidak ditemukan di Excel")
            else:
                st.session_state.master_data = df
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error file: {e}")
    st.stop()

# =======================
# Login Pegawai
# =======================
df = st.session_state.master_data
col_nama = next((c for c in df.columns if "NAMA" in c), None)

if 'user' not in st.session_state:
    st.title("🔐 Login E-LKH")
    nama_user = st.selectbox("Pilih Nama Anda:", ["-- Pilih --"] + sorted(df[col_nama].dropna().unique()))
    if st.button("Masuk Aplikasi") and nama_user != "-- Pilih --":
        row = df[df[col_nama] == nama_user].iloc[0]
        lbl_id, val_id = "NIP", "-"
        for c in df.columns:
            if "NIP" in c:
                clean_val = str(row.get(c, "")).replace(".0","").strip()
                if clean_val not in ["nan","-","","None"]:
                    lbl_id, val_id = c, clean_val
                    break
        st.session_state.user = {
            "nama": nama_user,
            "label_id": lbl_id,
            "no_id": val_id,
            "jabatan": str(row.get('JABATAN','Pegawai')),
            "atasan": "dr. Irana Priska",
            "nip_atasan": "19880929 201503 2 007"
        }
        st.experimental_rerun()

# =======================
# Dashboard
# =======================
if 'user' in st.session_state:
    u = st.session_state.user
    with st.sidebar:
        st.success(f"👤 {u['nama']}")
        st.caption(f"{u['label_id']}: {u['no_id']}")
        menu = st.radio("Menu:", ["📝 Input Harian", "📊 Rekap Bulanan"])
        if st.button("Keluar"):
            st.session_state.clear()
            st.experimental_rerun()

    if 'data_lkh' not in st.session_state:
        st.session_state.data_lkh = []

    # =======================
    # Input Harian
    # =======================
    if menu == "📝 Input Harian":
        st.header("📝 Input Aktivitas")
        with st.form("form_aktivitas"):
            tgl_input = st.date_input("Tanggal", datetime.now())
            jam_mulai = st.text_input("Jam Mulai", "08.00")
            jam_selesai = st.text_input("Jam Selesai", "14.00")
            uraian = st.text_area("Uraian Kegiatan", height=100)
            output = st.text_input("Output / Hasil", "1 Kegiatan")
            submitted = st.form_submit_button("💾 Tambah Aktivitas")
            if submitted:
                try:
                    t1 = parse_jam(jam_mulai)
                    t2 = parse_jam(jam_selesai)
                    if t2 <= t1:
                        st.error("Jam selesai harus lebih besar dari jam mulai")
                    else:
                        durasi = int((t2-t1).total_seconds()/60)
                        st.session_state.data_lkh.append({
                            "tgl": tgl_input.strftime("%Y-%m-%d"),
                            "hari": HARI_ID[tgl_input.strftime("%A")],
                            "jam": f"{jam_mulai} - {jam_selesai}",
                            "ket": uraian,
                            "out": output,
                            "durasi": durasi
                        })
                        st.toast("Data tersimpan ✅")
                        st.experimental_rerun()
                except:
                    st.error("Format jam salah. Gunakan 08.00 atau 08:00")

        # =======================
        # Tabel Harian
        # =======================
        if st.session_state.data_lkh:
            st.subheader("📄 LKH Harian")
            df_lkh = pd.DataFrame(st.session_state.data_lkh)
            for idx, row in df_lkh.iterrows():
                st.markdown(f"**{idx+1}. {row['tgl']} ({row['hari']})**")
                c1, c2 = st.columns([3,1])
                with c1:
                    st.write(f"Jam: {row['jam']}")
                    st.write(f"Kegiatan: {row['ket']}")
                    st.write(f"Output: {row['out']}")
                    st.write(f"Durasi: {row['durasi']} menit")
                with c2:
                    if st.button("✏️ Edit", key=f"edit{idx}"):
                        st.session_state.edit_index = idx
                    if st.button("🗑 Hapus", key=f"hapus{idx}"):
                        st.session_state.data_lkh.pop(idx)
                        st.toast("Data dihapus ✅")
                        st.experimental_rerun()

            # Popup Edit
            if 'edit_index' in st.session_state:
                idx = st.session_state.edit_index
                edit_row = st.session_state.data_lkh[idx]
                st.markdown("---")
                st.subheader(f"✏️ Edit Aktivitas {idx+1}")
                tgl_edit = st.date_input("Tanggal", datetime.strptime(edit_row['tgl'], "%Y-%m-%d"), key="tgl_edit")
                jam_mulai_edit = st.text_input("Jam Mulai", edit_row['jam'].split(" - ")[0], key="jm_edit")
                jam_selesai_edit = st.text_input("Jam Selesai", edit_row['jam'].split(" - ")[1], key="js_edit")
                uraian_edit = st.text_area("Uraian Kegiatan", edit_row['ket'], key="uraian_edit")
                output_edit = st.text_input("Output / Hasil", edit_row['out'], key="out_edit")
                if st.button("💾 Simpan Perubahan"):
                    try:
                        t1 = parse_jam(jam_mulai_edit)
                        t2 = parse_jam(jam_selesai_edit)
                        if t2 <= t1:
                            st.error("Jam selesai harus lebih besar dari jam mulai")
                        else:
                            durasi = int((t2-t1).total_seconds()/60)
                            st.session_state.data_lkh[idx] = {
                                "tgl": tgl_edit.strftime("%Y-%m-%d"),
                                "hari": HARI_ID[tgl_edit.strftime("%A")],
                                "jam": f"{jam_mulai_edit} - {jam_selesai_edit}",
                                "ket": uraian_edit,
                                "out": output_edit,
                                "durasi": durasi
                            }
                            st.toast("Data diperbarui ✅")
                            st.session_state.pop('edit_index')
                            st.experimental_rerun()
                    except:
                        st.error("Format jam salah. Gunakan 08.00 atau 08:00")

            # =======================
            # Export PDF Harian
            # =======================
            html_harian = "<h2>Laporan Harian</h2><table border=1><tr><th>No</th><th>Tanggal</th><th>Jam</th><th>Kegiatan</th><th>Output</th><th>Durasi</th></tr>"
            for i, r in enumerate(st.session_state.data_lkh):
                html_harian += f"<tr><td>{i+1}</td><td>{r['tgl']}</td><td>{r['jam']}</td><td>{r['ket']}</td><td>{r['out']}</td><td>{r['durasi']}</td></tr>"
            html_harian += "</table>"
            export_pdf(html_harian, filename=f"LKH_Harian_{u['nama']}.pdf")

    # =======================
    # Rekap Bulanan
    # =======================
    elif menu == "📊 Rekap Bulanan":
        st.header("📊 Rekap Bulanan")
        if not st.session_state.data_lkh:
            st.info("⚠️ Belum ada data")
        else:
            df_raw = pd.DataFrame(st.session_state.data_lkh)
            df_raw['tgl'] = pd.to_datetime(df_raw['tgl'])
            rekap = df_raw.groupby('tgl').agg({'durasi':'sum'}).reset_index().sort_values('tgl')
            TARGET_HARIAN = 270
            total_capaian = rekap['durasi'].sum()
            total_target = len(rekap)*TARGET_HARIAN
            persen = (total_capaian/total_target*100) if total_target>0 else 0
            bulan_laporan = BULAN_ID.get(rekap.iloc[0]['tgl'].month,"BULAN INI")
            
            st.markdown(f"**Bulan:** {bulan_laporan}")
            st.dataframe(rekap)
            st.markdown(f"**Total Capaian:** {total_capaian} menit / {total_target} menit ({persen:.2f}%)")

            # Export PDF Bulanan
            html_bulanan = "<h2>Rekap Bulanan</h2><table border=1><tr><th>No</th><th>Tanggal</th><th>Durasi</th><th>Target</th></tr>"
            for i, r in enumerate(rekap.itertuples()):
                html_bulanan += f"<tr><td>{i+1}</td><td>{r.tgl.strftime('%Y-%m-%d')}</td><td>{r.durasi}</td><td>{TARGET_HARIAN}</td></tr>"
            html_bulanan += f"<tr><td colspan=2>Total</td><td>{total_capaian}</td><td>{total_target}</td></tr></table>"
            export_pdf(html_bulanan, filename=f"Rekap_Bulanan_{u['nama']}.pdf")
