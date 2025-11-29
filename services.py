import os
import json
import traceback
from faster_whisper import WhisperModel
from llama_cpp import Llama

# Global model instances
whisper_model = None
llm_model = None
MODEL_FILENAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"

def load_models():
    global whisper_model, llm_model
    
    if whisper_model is None:
        print("Loading Whisper model...")
        model_path = "models/whisper-base"
        if os.path.exists(model_path):
            whisper_model = WhisperModel(model_path, device="cpu", compute_type="int8")
        else:
            # Fallback if not downloaded to specific path, though download_models.py should handle it
            whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            
    if llm_model is None:
        print("Loading LLM model...")
        model_path = os.path.join("models", MODEL_FILENAME)
        if os.path.exists(model_path):
            # n_ctx=4096 is better for conversation history
            llm_model = Llama(model_path=model_path, n_ctx=4096, verbose=False)
        else:
            print(f"LLM model not found at {model_path}")
            return False
            
    return True

def process_transcription(audio_path):
    """
    Transcribe full audio and format as dialogue using LLM.
    """
    try:
        if not load_models():
            return {"error": "Model AI belum didownload."}

        # 1. Check file size
        file_size = os.path.getsize(audio_path)
        print(f"Processing audio: {audio_path} (Size: {file_size} bytes)")
        
        if file_size < 1000:
            return {"error": "File audio terlalu kecil/kosong."}

        # 2. Convert to WAV
        wav_path = audio_path + ".wav"
        os.system(f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{wav_path}" -y')
        
        if not os.path.exists(wav_path):
            return {"error": "Gagal konversi audio (FFmpeg)."}

        # 3. Transcribe (Full)
        print("Transcribing full audio...")
        segments, info = whisper_model.transcribe(
            wav_path, 
            beam_size=5, 
            language="id",
            vad_filter=False
        )
        
        # Combine segments with timestamps to help LLM guess speakers
        raw_transcript = ""
        for segment in segments:
            raw_transcript += f"[{segment.start:.2f}s] {segment.text}\n"
            
        print(f"Raw Transcript Length: {len(raw_transcript)}")
        
        # Cleanup WAV
        if os.path.exists(wav_path):
            os.remove(wav_path)

        # 4. Format as Dialogue using LLM
        print("Formatting as dialogue...")
        messages = [
            {"role": "system", "content": "Anda adalah asisten transkripsi. Tugas Anda adalah mengubah teks mentah menjadi format dialog wawancara (P1 = Penanya, I1 = Informan/Narasumber)."},
            {"role": "user", "content": f"""
Berikut adalah transkrip mentah dari wawancara:

{raw_transcript}

Tugas:
1. Rapikan teks tersebut.
2. Ubah menjadi format dialog seperti ini:
   P1 : [Teks Penanya]
   I1 : [Teks Informan]
   
3. Jika sulit membedakan, gunakan perkiraan terbaik berdasarkan konteks tanya-jawab.
4. Output HANYA teks dialog. Jangan ada komentar lain.
"""}
        ]
        
        output = llm_model.create_chat_completion(
            messages=messages,
            max_tokens=2048,
            temperature=0.3
        )
        
        formatted_content = output['choices'][0]['message']['content'].strip()
        return {"content": formatted_content}
        
    except Exception as e:
        print(f"Error processing transcription: {e}")
        traceback.print_exc()
        return {"error": str(e)}

