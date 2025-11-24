import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def process_audio_with_gemini(audio_file_path):
    """
    Uploads audio to Gemini and requests a summary of health information.
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API Key not configured"}

    try:
        # Upload the file
        myfile = genai.upload_file(audio_file_path, mime_type="audio/webm")
        
        # Wait for file to be active
        import time
        while myfile.state.name == "PROCESSING":
            time.sleep(1)
            myfile = genai.get_file(myfile.name)
            
        if myfile.state.name != "ACTIVE":
            return {"error": f"File upload failed with state: {myfile.state.name}"}
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = """
        Dengarkan rekaman suara ini yang berisi keluhan kesehatan pengguna.
        Tolong ekstrak dan ringkas informasi berikut dalam format JSON:
        1. Keluhan Utama
        2. Gejala yang disebutkan
        3. Data vital (jika ada, seperti suhu, berat badan, tensi)
        4. Saran awal (jika bisa diberikan secara umum)
        
        Jika tidak ada informasi kesehatan, katakan 'Tidak ada informasi kesehatan terdeteksi'.
        """
        
        result = model.generate_content([myfile, prompt])
        return result.text
        
    except Exception as e:
        return {"error": str(e)}
