import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Laporan Kerja Harian", layout="wide")

# --- Inisialisasi State ---
if 'activities' not in st.session_state:
    st.session_state.activities = []

# --- Data Profil User (Dummy) ---
USER_PROFILE = {
    "name": "Budi Santoso",
    "nip": "19800101 200003 1 001",
    "position": "Pranata Komputer Ahli Muda",
    "unit": "Dinas Kominfo",
    "supervisor": "Dr. Siti Aminah",
    "supervisor_nip": "19750505 199903 2 005"
}

def calculate_duration(start, end):
    t1 = datetime.strptime(start, "%H:%M")
    t2 = datetime.strptime(end, "%H:%M")
    delta = t2 - t1
    return int(delta.total_seconds() / 60)

# --- JUDUL & HEADER ---
st.title("Laporan Kerja Harian")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Nama:** {USER_PROFILE['name']}")
    st.write(f"**NIP:** {USER_PROFILE['nip']}")
    st.write(f"**Jabatan:** {USER_PROFILE['position']}")

with col2:
    current_date = st.date_input("Tanggal", datetime.now())
    st.write(f"**Unit Kerja:** {USER_PROFILE['unit']}")
    st.write(f"**Hari:** {current_date.strftime('%A')}")

st.markdown("---")

# --- FORM INPUT AKTIVITAS ---
st.subheader("Tambah Aktivitas")
with st.form("activity_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns([1, 1, 3, 1])
    with c1:
        start_time = st.time_input("Mulai", datetime.strptime("07:30", "%H:%M"))
    with c2:
        end_time = st.time_input("Selesai", datetime.strptime("08:30", "%H:%M"))
    with c3:
        desc = st.text_input("Uraian Kegiatan")
    with c4:
        output = st.text_input("Output", "1 Kegiatan")
    
    submitted = st.form_submit_button("Simpan Aktivitas")

    if submitted:
        if desc:
            s_str = start_time.strftime("%H:%M")
            e_str = end_time.strftime("%H:%M")
            
            if s_str >= e_str:
                st.error("Waktu selesai harus lebih besar dari waktu mulai.")
            else:
                durasi = calculate_duration(s_str, e_str)
                new_act = {
                    "Waktu": f"{s_str} - {e_str}",
                    "Uraian Kegiatan": desc,
                    "Output": output,
                    "Durasi (Menit)": durasi
                }
                st.session_state.activities.append(new_act)
                st.success("Aktivitas ditambahkan!")
                st.rerun()
        else:
            st.warning("Uraian kegiatan tidak boleh kosong.")

# --- TABEL AKTIVITAS ---
st.subheader("Daftar Kegiatan")

if st.session_state.activities:
    df = pd.DataFrame(st.session_state.activities)
    
    # Menghitung Total Durasi
    total_durasi = df["Durasi (Menit)"].sum()
    
    # Tampilkan Tabel
    st.table(df)
    
    st.markdown(f"### Total Durasi Kerja Efektif: **{total_durasi} Menit**")
    
    # Tombol Hapus (Reset)
    if st.button("Hapus Semua Data"):
        st.session_state.activities = []
        st.rerun()

else:
    st.info("Belum ada aktivitas yang dicatat hari ini.")

# --- FITUR CETAK (Sederhana untuk Streamlit) ---
# Streamlit sulit melakukan 'print' browser langsung seperti React.
# Solusinya biasanya membuat CSV atau PDF download.
if st.session_state.activities:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Laporan (CSV)",
        data=csv,
        file_name=f"lkh_{USER_PROFILE['nip']}_{current_date}.csv",
        mime='text/csv',
    )
