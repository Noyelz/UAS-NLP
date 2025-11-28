import traceback
import sys

print("Starting test...")

try:
    import faster_whisper
    print("faster_whisper imported path:", faster_whisper.__file__)
    from faster_whisper import WhisperModel
    print("WhisperModel imported.")
except ImportError:
    print("Failed to import faster_whisper")
    traceback.print_exc()
except Exception:
    print("Error importing faster_whisper")
    traceback.print_exc()

try:
    import llama_cpp
    print("llama_cpp imported path:", llama_cpp.__file__)
    from llama_cpp import Llama
    print("Llama imported.")
except ImportError:
    print("Failed to import llama_cpp")
    traceback.print_exc()
except Exception:
    print("Error importing llama_cpp")
    traceback.print_exc()
