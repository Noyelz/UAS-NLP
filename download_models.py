import os
import sys
from huggingface_hub import hf_hub_download, snapshot_download

# Force stdout flush for real-time logs
sys.stdout.reconfigure(line_buffering=True)

def download_models():
    print("Initializing download process...")
    print("Make sure you have a stable internet connection.")
    os.makedirs("models", exist_ok=True)

    # 1. Download Llama 3.2 3B Instruct GGUF (Better than TinyLlama)
    print("\n[1/2] Downloading Llama-3.2-3B-Instruct GGUF...")
    # Using bartowski's quantization which is reliable
    model_name = "bartowski/Llama-3.2-3B-Instruct-GGUF"
    filename = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    try:
        path = hf_hub_download(repo_id=model_name, filename=filename, local_dir="models", local_dir_use_symlinks=False)
        print(f"LLM downloaded to: {path}")
    except Exception as e:
        print(f"Error downloading LLM: {e}")

    # 2. Download Whisper Model (Base)
    print("Downloading Whisper Base model...")
    try:
        # Use explicit repo_id for faster-whisper converted model
        # Download to models/whisper-base
        from huggingface_hub import snapshot_download
        
        model_id = "systran/faster-whisper-base"
        snapshot_download(repo_id=model_id, local_dir="models/whisper-base", local_dir_use_symlinks=False)
        print("Whisper model downloaded.")
    except Exception as e:
        print(f"Error downloading Whisper: {e}")

if __name__ == "__main__":
    download_models()
