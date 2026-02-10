import speech_recognition as sr
import edge_tts
import asyncio
import os

# --- 1. SPEECH TO TEXT (File Based) ---
def transcribe_audio(audio_file_path):
    """
    Takes an audio file path (WAV), reads it, and sends it to Google Free STT.
    """
    recognizer = sr.Recognizer()
    
    try:
        # Use AudioFile instead of Microphone
        with sr.AudioFile(audio_file_path) as source:
            # We don't need adjust_for_ambient_noise for direct files usually, 
            # but it doesn't hurt.
            audio_data = recognizer.record(source)
            
        text = recognizer.recognize_google(audio_data)
        return text.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "API Error"
    except Exception as e:
        return f"Error: {e}"

# --- 2. TEXT TO SPEECH (Bytes Based) ---
async def generate_audio_bytes(text, voice="en-GB-RyanNeural"):
    """
    Generates audio and returns the bytes directly (no file saving needed if possible, 
    but edge-tts saves to file easily, so we read it back).
    """
    temp_file = "temp_response.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_file)
    
    # Read the file back into memory
    with open(temp_file, "rb") as f:
        audio_bytes = f.read()
    
    # Clean up
    os.remove(temp_file)
    return audio_bytes

def get_audio_response(text):
    """
    Synchronous wrapper for the async generator.
    """
    return asyncio.run(generate_audio_bytes(text))