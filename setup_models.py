import os
import sys
from faster_whisper import download_model
from huggingface_hub import hf_hub_download

# Konfigurasi LLM
LLM_REPO = "bartowski/Llama-3.2-3B-Instruct-GGUF"
LLM_FILENAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
LLM_DIR = "models"

def check_and_download_whisper():
    print("\n" + "="*50)
    print(" [1/2] MEMERIKSA MODEL WHISPER (MEDIUM) ")
    print("="*50)
    try:
        # download_model akan cek cache dulu. Jika belum ada, dia download dengan progress bar.
        # Jika sudah ada, dia cuma verifikasi sebentar.
        print("Memeriksa cache model Whisper...")
        path = download_model("medium")
        print(f"✅ Model Whisper SIAP di: {path}")
    except Exception as e:
        print(f"❌ Gagal memproses Whisper: {e}")
        sys.exit(1)

def check_and_download_llm():
    print("\n" + "="*50)
    print(" [2/2] MEMERIKSA MODEL LLM (Llama 3.2) ")
    print("="*50)
    
    if not os.path.exists(LLM_DIR):
        os.makedirs(LLM_DIR)
        
    file_path = os.path.join(LLM_DIR, LLM_FILENAME)
    
    if os.path.exists(file_path):
        print(f"✅ Model LLM sudah ada di: {file_path}")
        print("   (Hapus file tersebut jika ingin mendownload ulang)")
        return

    print(f"Model belum ditemukan. Memulai download dari {LLM_REPO}...")
    print("Ukuran file sekitar 2.0 GB. Mohon tunggu...")
    
    try:
        hf_hub_download(
            repo_id=LLM_REPO,
            filename=LLM_FILENAME,
            local_dir=LLM_DIR,
            local_dir_use_symlinks=False # Pastikan file asli terdownload
        )
        print(f"✅ Model LLM BERHASIL didownload.")
    except Exception as e:
        print(f"❌ Gagal download LLM: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n=== SYSTEM CHECK & SETUP ===")
    check_and_download_whisper()
    check_and_download_llm()
    print("\n=== SEMUA MODEL SIAP! MEMULAI APLIKASI... ===\n")
