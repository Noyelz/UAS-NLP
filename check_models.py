import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    with open('available_models.txt', 'w') as f:
        f.write("API Key not found")
else:
    genai.configure(api_key=api_key)
    try:
        with open('available_models.txt', 'w') as f:
            f.write("--- AVAILABLE MODELS ---\n")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
            f.write("--- END OF LIST ---\n")
    except Exception as e:
        with open('available_models.txt', 'w') as f:
            f.write(f"Error: {e}")
