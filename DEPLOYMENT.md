# Panduan Deployment (Instalasi di Laptop Lain)

Aplikasi ini menggunakan **Llama 3.2** yang membutuhkan library khusus. Cara paling stabil dan mudah untuk menjalankannya di Windows (tanpa menginstall Visual Studio Build Tools yang berukuran bergiga-giga) adalah menggunakan **Miniconda**.

## Langkah-langkah:

### 1. Persiapan di Laptop Target
1.  Download **Miniconda** (Pilih "Miniconda3 Windows 64-bit"):
    *   Link: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2.  Install Miniconda (Next, Next, Finish).
    *   **PENTING**: Saat instalasi, jika ada pilihan "Add Miniconda3 to my PATH environment variable", **CENTANG** pilihan tersebut (meskipun ada tulisan not recommended, ini memudahkan jalannya script).

### 2. Copy Aplikasi
1.  Copy seluruh folder `UAS NLP` ke laptop target.

### 3. Instalasi Otomatis
1.  Buka folder tersebut di laptop target.
2.  Double-click file **`setup.bat`**.
3.  Tunggu proses instalasi selesai (akan mendownload model dan library).

### 4. Menjalankan Aplikasi
Setiap kali ingin menjalankan aplikasi:
1.  Buka terminal (Command Prompt) di folder tersebut.
2.  Ketik: `conda activate healthvoice_new`
3.  Ketik: `python app.py`

---
**Catatan:**
Jika `setup.bat` gagal karena koneksi internet, coba jalankan lagi. Script sudah dilengkapi fitur resume/retry.
