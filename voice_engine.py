import speech_recognition as sr
import edge_tts
import asyncio
import io

# --- 1. THE EARS (Speech to Text) ---
def transcribe_audio(file_path):
    """
    Transcribes a WAV file from the UI.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Transcription Error: {e}")
        return None

# --- 2. THE MOUTH (Text to Speech) ---
async def _generate_audio(text, voice="en-GB-RyanNeural"):
    """
    Generates audio bytes in memory (no files needed).
    """
    communicate = edge_tts.Communicate(text, voice)
    # capturing the audio stream into memory
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    
    audio_stream.seek(0)
    return audio_stream

def get_audio_response(text):
    """
    Synchronous wrapper that returns the audio data as bytes.
    """
    try:
        audio_io = asyncio.run(_generate_audio(text))
        return audio_io
    except Exception as e:
        print(f"TTS Error: {e}")
        return None