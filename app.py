

import React, { useState, useEffect } from 'react';
import type { DailyReport, Activity, UserProfile } from '../types';
// FIX: Use submodule imports for date-fns to fix export errors.
import { format, differenceInMinutes } from 'date-fns';
import parseISO from 'date-fns/parseISO';
import parse from 'date-fns/parse';
import id from 'date-fns/locale/id';

interface DailyReportModalProps {
    date: Date;
    report?: DailyReport;
    onClose: () => void;
    onSave: (date: Date, activities: Activity[]) => void;
    userProfile: UserProfile;
}

const DailyReportModal: React.FC<DailyReportModalProps> = ({ date, report, onClose, onSave, userProfile }) => {
    const [activities, setActivities] = useState<Activity[]>([]);
    const [newActivity, setNewActivity] = useState({
        startTime: '07:45',
        endTime: '08:30',
        description: '',
        output: '1 Kegiatan'
    });

    useEffect(() => {
        if (report) {
            setActivities(report.activities);
        }
    }, [report]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setNewActivity(prev => ({ ...prev, [name]: value }));
    };

    const handleAddActivity = () => {
        if (!newActivity.description.trim()) {
            alert('Deskripsi aktivitas tidak boleh kosong.');
            return;
        }

        try {
            const startDate = parse(newActivity.startTime, 'HH:mm', date);
            const endDate = parse(newActivity.endTime, 'HH:mm', date);
            
            if (endDate <= startDate) {
                alert('Waktu selesai harus setelah waktu mulai.');
                return;
            }

            const duration = differenceInMinutes(endDate, startDate);

            const activityToAdd: Activity = {
                id: crypto.randomUUID(),
                ...newActivity,
                duration
            };
            setActivities(prev => [...prev, activityToAdd]);
            setNewActivity({ startTime: newActivity.endTime, endTime: '', description: '', output: '1 Kegiatan' });
        } catch(e) {
            alert("Format waktu tidak valid. Gunakan HH:mm.");
        }
    };
    
    const handleDeleteActivity = (id: string) => {
        setActivities(prev => prev.filter(act => act.id !== id));
    };

    const handleSaveReport = () => {
        onSave(date, activities);
    };
    
    const handlePrint = () => {
        const printContents = document.getElementById('daily-report-printable')?.innerHTML;
        const originalContents = document.body.innerHTML;
        if (printContents) {
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            // Re-mount the app to restore functionality after printing
            window.location.reload();
        }
    };

    const totalDuration = activities.reduce((sum, act) => sum + act.duration, 0);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-start pt-10 z-20 overflow-auto no-print">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl p-8 m-4">
                <div id="daily-report-printable">
                    <div className="text-center mb-6">
                        <h2 className="text-xl font-bold uppercase">Laporan Kerja Harian</h2>
                    </div>

                    <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-sm mb-6">
                        <div className="flex"><span className="w-28">BULAN</span>: <span className="uppercase">{format(date, 'MMMM', { locale: id })}</span></div>
                        <div className="flex"><span className="w-28">NAMA</span>: {userProfile.name}</div>
                        <div className="flex"><span className="w-28">HARI</span>: {format(date, 'EEEE', { locale: id })}</div>
                        <div className="flex"><span className="w-28">NIP</span>: {userProfile.nip}</div>
                        <div className="flex"><span className="w-28">TANGGAL</span>: {format(date, 'd', { locale: id })}</div>
                        <div className="flex"><span className="w-28">JABATAN</span>: {userProfile.position}</div>
                        <div></div>
                        <div className="flex"><span className="w-28">UNIT KERJA</span>: {userProfile.unit}</div>
                    </div>
                    
                    {/* Display Activities */}
                    <table className="w-full border-collapse border border-black text-sm">
                        <thead className="bg-gray-200 text-center font-bold">
                            <tr>
                                <td className="border border-black p-2 w-12">NO</td>
                                <td className="border border-black p-2 w-48">WAKTU</td>
                                <td className="border border-black p-2">AKTIVITAS</td>
                                <td className="border border-black p-2 w-32">OUTPUT</td>
                                <td className="border border-black p-2 w-32">DURASI (MENIT)</td>
                                <td className="border border-black p-2 w-16 no-print">AKSI</td>
                            </tr>
                        </thead>
                        <tbody>
                            {activities.map((act, index) => (
                                <tr key={act.id}>
                                    <td className="border border-black p-2 text-center">{index + 1}</td>
                                    <td className="border border-black p-2 text-center">{act.startTime} - {act.endTime}</td>
                                    <td className="border border-black p-2">{act.description}</td>
                                    <td className="border border-black p-2 text-center">{act.output}</td>
                                    <td className="border border-black p-2 text-center">{act.duration}</td>
                                    <td className="border border-black p-2 text-center no-print">
                                        <button onClick={() => handleDeleteActivity(act.id)} className="text-red-500 hover:text-red-700">&times;</button>
                                    </td>
                                </tr>
                            ))}
                            <tr className="font-bold">
                                <td colSpan={4} className="border border-black p-2 text-center">JUMLAH</td>
                                <td className="border border-black p-2 text-center">{totalDuration}</td>
                                <td className="border border-black no-print"></td>
                            </tr>
                        </tbody>
                    </table>

                     <div className="mt-12 grid grid-cols-2 gap-8 text-center text-sm">
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

                {/* Form to Add New Activity */}
                <div className="mt-8 pt-6 border-t no-print">
                     <h3 className="text-lg font-semibold mb-3">Tambah Aktivitas Baru</h3>
                     <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                        <div className="col-span-2 grid grid-cols-2 gap-2">
                             <div>
                                <label className="block text-sm font-medium text-gray-700">Mulai</label>
                                <input type="time" name="startTime" value={newActivity.startTime} onChange={handleInputChange} className="mt-1 w-full p-2 border rounded"/>
                             </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700">Selesai</label>
                                <input type="time" name="endTime" value={newActivity.endTime} onChange={handleInputChange} className="mt-1 w-full p-2 border rounded"/>
                             </div>
                        </div>
                        <div className="col-span-2">
                             <label className="block text-sm font-medium text-gray-700">Deskripsi Aktivitas</label>
                            <input name="description" value={newActivity.description} onChange={handleInputChange} className="mt-1 w-full p-2 border rounded"/>
                        </div>
                        <div>
                            <button onClick={handleAddActivity} className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Tambah</button>
                        </div>
                    </div>
                </div>

                <div className="mt-8 flex justify-end space-x-3 no-print">
                    <button onClick={onClose} className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400">Tutup</button>
                    <button onClick={handlePrint} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Cetak Harian</button>
                    <button onClick={handleSaveReport} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Simpan & Tutup</button>
                </div>
            </div>
        </div>
    );
};

export default DailyReportModal;
