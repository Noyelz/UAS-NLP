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

def process_interview_step(audio_path, question):
    """
    Process a single interview step: Audio -> Text -> (Optional Refinement)
    For local, we primarily need the transcription.
    """
    try:
        if not load_models():
            return {"error": "Model AI belum didownload. Jalankan download_models.py."}

        # 1. Check file size
        file_size = os.path.getsize(audio_path)
        print(f"Processing audio: {audio_path} (Size: {file_size} bytes)")
        
        if file_size < 1000: # Less than 1KB is likely empty/silence
            print("Audio file too small, returning empty.")
            return {"text": "Tidak terdengar suara."}

        # 2. Convert to WAV using ffmpeg (Force conversion to avoid container issues)
        wav_path = audio_path + ".wav"
        os.system(f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{wav_path}" -y')
        
        if not os.path.exists(wav_path):
            print("FFmpeg conversion failed.")
            return {"error": "Gagal memproses audio (FFmpeg error)."}

        # 3. Transcribe
        # Try with VAD disabled and specific parameters for short audio
        print("Transcribing with language='id' and vad_filter=False...")
        segments, info = whisper_model.transcribe(
            wav_path, 
            beam_size=5, 
            language="id",
            vad_filter=False,
            condition_on_previous_text=False
        )
        transcribed_text = " ".join([segment.text for segment in segments]).strip()
        print(f"Transcribed text (ID): '{transcribed_text}'")
        
        # Fallback: Auto-detect language if empty
        if not transcribed_text:
            print("Retrying with auto language detection...")
            segments, info = whisper_model.transcribe(
                wav_path, 
                beam_size=5, 
                vad_filter=False
            )
            transcribed_text = " ".join([segment.text for segment in segments]).strip()
            print(f"Transcribed text (Auto): '{transcribed_text}'")

        # Cleanup WAV
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        if not transcribed_text:
            return {"text": "Tidak terdengar suara."}
            
        return {"text": transcribed_text}
        
    except Exception as e:
        print(f"Error processing step: {e}")
        traceback.print_exc()
        return {"error": str(e)}

def generate_final_summary(answers):
    """
    Generate final JSON summary from all answers using local LLM.
    """
    try:
        if not load_models():
            return {"error": "Model AI belum didownload."}

        answers_str = json.dumps(answers, indent=2, ensure_ascii=False)
        
        # Prompt for Llama 3 / Instruct models
        # Llama 3 uses specific tokens: <|begin_of_text|><|start_header_id|>system<|end_header_id|> ...
        # But llama-cpp-python might handle chat format if we use create_chat_completion, 
        # or we can just use a raw prompt. Let's use raw prompt for control or create_chat_completion if available.
        
        # Using standard chat format for Llama 3
        messages = [
            {"role": "system", "content": "Anda adalah asisten medis AI. Analisis jawaban pasien TB dan buat ringkasan JSON."},
            {"role": "user", "content": f"""
Berikut adalah hasil wawancara dengan pasien Tuberculosis (TB):

{answers_str}

Tugas Anda:
1. Analisis jawaban-jawaban tersebut.
2. Buat ringkasan medis dalam format JSON.
3. Format JSON harus memiliki key:
    - "keluhan_utama": Ringkasan keluhan utama.
    - "gejala": Daftar gejala yang terdeteksi (batuk, demam, dll).
    - "data_vital": Data angka jika ada (suhu, berat badan).
    - "analisis_tb": Analisis risiko TB berdasarkan jawaban (Rendah/Sedang/Tinggi) dan alasannya.
    - "saran": Saran medis selanjutnya.

Output HANYA JSON. Jangan ada teks lain.
"""}
        ]
        
        output = llm_model.create_chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.2,
            response_format={"type": "json_object"} # Llama.cpp python supports this for some models/versions
        )
        
        result_text = output['choices'][0]['message']['content'].strip()
        
        # Clean up if needed (sometimes it adds markdown)
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        try:
            return json.loads(result_text)
        except:
            # Fallback parsing
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(result_text[start:end])
            else:
                return {"error": "Gagal parsing JSON", "raw": result_text}
        
    except Exception as e:
        print(f"Error in generate_final_summary: {e}")
        return {
            "keluhan_utama": "Gagal memproses summary",
            "gejala": [],
            "data_vital": "N/A",
            "analisis_tb": "Error",
            "saran": "Silakan konsultasi langsung."
        }

