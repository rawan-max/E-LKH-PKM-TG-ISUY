import React, { useState, useEffect, useMemo } from 'react';
// Pastikan path ini sesuai dengan struktur project Anda
import type { DailyReport, Activity, UserProfile } from '../types'; 
import { format, differenceInMinutes, parse, isValid } from 'date-fns';
import { id as localeId } from 'date-fns/locale';

interface DailyReportModalProps {
    date: Date;
    report?: DailyReport;
    onClose: () => void;
    onSave: (date: Date, activities: Activity[]) => void;
    userProfile: UserProfile;
}

const DailyReportModal: React.FC<DailyReportModalProps> = ({ 
    date, 
    report, 
    onClose, 
    onSave, 
    userProfile 
}) => {
    // State untuk daftar aktivitas
    const [activities, setActivities] = useState<Activity[]>([]);
    
    // State untuk form input
    const [formState, setFormState] = useState({
        startTime: '07:30',
        endTime: '08:30',
        description: '',
        output: '1 Kegiatan'
    });

    // State untuk mode edit
    const [editingId, setEditingId] = useState<string | null>(null);

    // Load data awal jika ada report
    useEffect(() => {
        if (report && report.activities) {
            setActivities(report.activities);
        }
    }, [report]);

    // Sorting activities otomatis berdasarkan waktu mulai
    const sortedActivities = useMemo(() => {
        return [...activities].sort((a, b) => a.startTime.localeCompare(b.startTime));
    }, [activities]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormState(prev => ({ ...prev, [name]: value }));
    };

    const resetForm = (lastEndTime?: string) => {
        setFormState({
            startTime: lastEndTime || '08:00',
            endTime: '',
            description: '',
            output: '1 Kegiatan'
        });
        setEditingId(null);
    };

    const handleSaveActivity = () => {
        // 1. Validasi Input Dasar
        if (!formState.description.trim()) {
            alert('Deskripsi aktivitas tidak boleh kosong.');
            return;
        }
        if (!formState.startTime || !formState.endTime) {
            alert('Waktu mulai dan selesai harus diisi.');
            return;
        }

        try {
            // 2. Validasi Logika Waktu
            const dateBase = date; // Menggunakan tanggal dari props
            const startObj = parse(formState.startTime, 'HH:mm', dateBase);
            const endObj = parse(formState.endTime, 'HH:mm', dateBase);

            if (!isValid(startObj) || !isValid(endObj)) {
                alert('Format waktu tidak valid.');
                return;
            }

            if (endObj <= startObj) {
                alert('Waktu selesai harus lebih besar dari waktu mulai.');
                return;
            }

            const duration = differenceInMinutes(endObj, startObj);

            if (editingId) {
                // UPDATE existing activity
                setActivities(prev => prev.map(act => 
                    act.id === editingId 
                        ? { ...act, ...formState, duration } 
                        : act
                ));
                resetForm(); // Reset form tanpa set start time
            } else {
                // CREATE new activity
                const newActivity: Activity = {
                    id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(), // Fallback untuk browser lama
                    ...formState,
                    duration
                };
                setActivities(prev => [...prev, newActivity]);
                
                // UX: Set start time berikutnya = end time aktivitas ini
                resetForm(formState.endTime);
            }

        } catch (error) {
            console.error(error);
            alert("Terjadi kesalahan saat memproses waktu.");
        }
    };

    const handleEditClick = (activity: Activity) => {
        setFormState({
            startTime: activity.startTime,
            endTime: activity.endTime,
            description: activity.description,
            output: activity.output
        });
        setEditingId(activity.id);
    };

    const handleDeleteActivity = (id: string) => {
        if (window.confirm("Hapus aktivitas ini?")) {
            setActivities(prev => prev.filter(act => act.id !== id));
            if (editingId === id) resetForm();
        }
    };

    const handleSaveReport = () => {
        onSave(date, sortedActivities);
    };

    const handlePrint = () => {
        window.print();
    };

    const totalDuration = activities.reduce((sum, act) => sum + act.duration, 0);

    return (
        // Wrapper Modal
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-start pt-10 z-50 overflow-y-auto print:p-0 print:bg-white print:static print:block">
            
            {/* Kontainer Utama */}
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl p-8 m-4 relative print:shadow-none print:w-full print:max-w-none print:m-0 print:p-0">
                
                {/* Tombol Close (Hidden saat print) */}
                <button 
                    onClick={onClose} 
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 print:hidden text-2xl font-bold"
                >
                    &times;
                </button>

                {/* --- AREA YANG AKAN DICETAK --- */}
                <div id="daily-report-printable" className="print:w-full">
                    {/* Header */}
                    <div className="text-center mb-6">
                        <h2 className="text-xl font-bold uppercase underline">Laporan Kerja Harian</h2>
                    </div>

                    {/* Identitas */}
                    <div className="grid grid-cols-2 gap-x-12 gap-y-1 text-sm mb-6">
                        <div className="flex"><span className="w-24 font-semibold">BULAN</span>: <span className="uppercase">{format(date, 'MMMM', { locale: localeId })}</span></div>
                        <div className="flex"><span className="w-24 font-semibold">NAMA</span>: {userProfile.name}</div>
                        
                        <div className="flex"><span className="w-24 font-semibold">HARI</span>: {format(date, 'EEEE', { locale: localeId })}</div>
                        <div className="flex"><span className="w-24 font-semibold">NIP</span>: {userProfile.nip}</div>
                        
                        <div className="flex"><span className="w-24 font-semibold">TANGGAL</span>: {format(date, 'd', { locale: localeId })}</div>
                        <div className="flex"><span className="w-24 font-semibold">JABATAN</span>: {userProfile.position}</div>
                        
                        <div></div> {/* Spacer */}
                        <div className="flex"><span className="w-24 font-semibold">UNIT KERJA</span>: {userProfile.unit}</div>
                    </div>
                    
                    {/* Tabel Aktivitas */}
                    <table className="w-full border-collapse border border-black text-sm">
                        <thead className="bg-gray-100 text-center font-bold">
                            <tr>
                                <td className="border border-black p-2 w-12">NO</td>
                                <td className="border border-black p-2 w-32">WAKTU</td>
                                <td className="border border-black p-2">URAIAN KEGIATAN</td>
                                <td className="border border-black p-2 w-28">OUTPUT</td>
                                <td className="border border-black p-2 w-24">DURASI (Mnt)</td>
                                <td className="border border-black p-2 w-20 print:hidden">AKSI</td>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedActivities.length > 0 ? (
                                sortedActivities.map((act, index) => (
                                    <tr key={act.id} className={editingId === act.id ? "bg-blue-50" : ""}>
                                        <td className="border border-black p-2 text-center align-top">{index + 1}</td>
                                        <td className="border border-black p-2 text-center align-top whitespace-nowrap">
                                            {act.startTime} - {act.endTime}
                                        </td>
                                        <td className="border border-black p-2 align-top text-justify">{act.description}</td>
                                        <td className="border border-black p-2 text-center align-top">{act.output}</td>
                                        <td className="border border-black p-2 text-center align-top">{act.duration}</td>
                                        <td className="border border-black p-2 text-center align-top print:hidden">
                                            <div className="flex justify-center space-x-2">
                                                <button 
                                                    onClick={() => handleEditClick(act)} 
                                                    className="text-blue-600 hover:text-blue-800 text-xs font-semibold"
                                                    title="Edit"
                                                >
                                                    Edit
                                                </button>
                                                <span className="text-gray-300">|</span>
                                                <button 
                                                    onClick={() => handleDeleteActivity(act.id)} 
                                                    className="text-red-500 hover:text-red-700 text-xs font-semibold"
                                                    title="Hapus"
                                                >
                                                    Hapus
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={6} className="border border-black p-4 text-center text-gray-500 italic">
                                        Belum ada aktivitas yang dicatat.
                                    </td>
                                </tr>
                            )}
                            <tr className="font-bold bg-gray-50">
                                <td colSpan={4} className="border border-black p-2 text-center">TOTAL DURASI KERJA EFEKTIF</td>
                                <td className="border border-black p-2 text-center">{totalDuration}</td>
                                <td className="border border-black print:hidden"></td>
                            </tr>
                        </tbody>
                    </table>

                    {/* Footer Tanda Tangan */}
                    <div className="mt-12 grid grid-cols-2 gap-8 text-center text-sm break-inside-avoid">
                        <div>
                            <p>Menyetujui</p>
                            <p>Pejabat Penilai/ Atasan Langsung</p>
                            <div className="h-24"></div>
                            <p className="font-bold underline">{userProfile.supervisorName}</p>
                            <p>NIP. {userProfile.supervisorNip}</p>
                        </div>
                        <div>
                            <p className="invisible">.</p>
                            <p>{userProfile.position}</p>
                            <div className="h-24"></div>
                            <p className="font-bold underline">{userProfile.name}</p>
                            <p>NIP. {userProfile.nip}</p>
                        </div>
                    </div>
                </div>
                {/* --- END AREA CETAK --- */}


                {/* --- AREA FORM INPUT (Hidden saat print) --- */}
                <div className="mt-8 pt-6 border-t border-gray-200 print:hidden">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-gray-800">
                            {editingId ? "Edit Aktivitas" : "Tambah Aktivitas Baru"}
                        </h3>
                        {editingId && (
                            <button onClick={() => resetForm()} className="text-sm text-gray-500 hover:text-gray-700 underline">
                                Batal Edit
                            </button>
                        )}
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
                            {/* Input Waktu */}
                            <div className="md:col-span-3 grid grid-cols-2 gap-2">
                                <div>
                                    <label className="block text-xs font-bold text-gray-600 mb-1">Mulai</label>
                                    <input 
                                        type="time" 
                                        name="startTime" 
                                        value={formState.startTime} 
                                        onChange={handleInputChange} 
                                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-600 mb-1">Selesai</label>
                                    <input 
                                        type="time" 
                                        name="endTime" 
                                        value={formState.endTime} 
                                        onChange={handleInputChange} 
                                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>
                            
                            {/* Input Output */}
                             <div className="md:col-span-2">
                                <label className="block text-xs font-bold text-gray-600 mb-1">Output</label>
                                <input 
                                    type="text"
                                    name="output" 
                                    value={formState.output} 
                                    onChange={handleInputChange} 
                                    placeholder="Contoh: 1 Dokumen"
                                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>

                            {/* Input Deskripsi */}
                            <div className="md:col-span-5">
                                <label className="block text-xs font-bold text-gray-600 mb-1">Uraian Kegiatan</label>
                                <input 
                                    type="text"
                                    name="description" 
                                    value={formState.description} 
                                    onChange={handleInputChange} 
                                    placeholder="Masukkan detail aktivitas..."
                                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    onKeyDown={(e) => e.key === 'Enter' && handleSaveActivity()}
                                />
                            </div>

                            {/* Tombol Aksi */}
                            <div className="md:col-span-2">
                                <button 
                                    onClick={handleSaveActivity} 
                                    className={`w-full px-4 py-2 text-white font-semibold rounded shadow transition-colors ${
                                        editingId ? 'bg-orange-500 hover:bg-orange-600' : 'bg-blue-600 hover:bg-blue-700'
                                    }`}
                                >
                                    {editingId ? 'Update' : 'Tambah'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Buttons */}
                <div className="mt-8 flex justify-end space-x-3 print:hidden">
                    <button onClick={onClose} className="px-5 py-2.5 bg-gray-200 text-gray-800 font-medium rounded hover:bg-gray-300 transition">
                        Tutup
                    </button>
                    <button onClick={handlePrint} className="px-5 py-2.5 bg-green-600 text-white font-medium rounded hover:bg-green-700 shadow flex items-center gap-2 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                        </svg>
                        Cetak PDF
                    </button>
                    <button onClick={handleSaveReport} className="px-5 py-2.5 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 shadow transition">
                        Simpan Laporan
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DailyReportModal;
