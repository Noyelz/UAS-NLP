# HealthVoice - AI Medical Transcription System

**HealthVoice** adalah sistem transkripsi cerdas yang dirancang untuk membantu tenaga medis dan peneliti dalam mendokumentasikan wawancara pasien (khususnya Tuberculosis). Sistem ini menggunakan kecerdasan buatan (AI) untuk mengubah rekaman suara menjadi teks dialog yang terstruktur.

![HealthVoice Dashboard](https://via.placeholder.com/800x400?text=HealthVoice+Dashboard+Preview)

## 🚀 Fitur Utama

*   **Transkripsi Otomatis**: Menggunakan **Whisper** (Faster-Whisper) untuk akurasi tinggi dalam Bahasa Indonesia.
*   **Format Dialog Cerdas**: Menggunakan **Llama 3.2** untuk mengubah teks mentah menjadi format dialog (P1: Penanya, I1: Informan).
*   **Sistem Admin Bertingkat**:
    *   **Admin I (Biasa)**: Merekam dan memproses transkripsi.
    *   **Admin II (Boss)**: Melihat dan mendownload semua hasil transkripsi.
    *   **Admin III (Super)**: Manajemen user dan hak akses penuh.
*   **Desain Modern**: Antarmuka "Soft Theme" yang ramah pengguna.

## 🛠️ Cara Instalasi (Deployment)

Aplikasi ini dirancang agar mudah diinstall di Windows tanpa perlu konfigurasi manual yang rumit.

### Prasyarat
*   Laptop Windows (64-bit).
*   **Miniconda** atau **Anaconda** sudah terinstall.
    *   *Jika belum ada, download di: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)*

### Langkah Instalasi
1.  **Clone/Download** repository ini.
2.  Buka folder project.
3.  Double-click file **`setup.bat`**.

Script ini akan otomatis:
*   Mengecek apakah Conda sudah terinstall.
*   Membuat environment Python baru (`healthvoice_new`).
*   Menginstall semua library yang dibutuhkan (termasuk driver AI).
*   Mendownload model AI (Llama 3.2 & Whisper) jika belum ada.

## 💻 Cara Penggunaan

Setiap kali ingin menjalankan aplikasi:

1.  Buka folder project.
2.  Jalankan **`setup.bat`** (Script ini pintar, jika sudah terinstall dia akan langsung menjalankan aplikasi).
3.  Buka browser dan akses: `http://127.0.0.1:5000`

### Akun Bawaan (Default)
Saat pertama kali dijalankan, sistem akan membuat akun Super Admin:
*   **Username**: `adminsuper`
*   **Password**: `adminsuper321`

Gunakan akun ini untuk login pertama kali dan mengatur user lain.

## 📂 Struktur Project
*   `app.py`: Entry point aplikasi.
*   `services.py`: Logika AI (Whisper & Llama).
*   `routes.py`: Pengaturan halaman dan API.
*   `models.py`: Struktur database.
*   `setup.bat`: Script instalasi otomatis.

---
*Dibuat untuk Tugas UAS NLP.*
