import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import os

# --- 1. THE EARS (Speech to Text) ---
def listen_to_microphone():
    """
    Listens to the default microphone and returns the text.
    Uses Google's Free Speech Recognition API.
    """
    recognizer = sr.Recognizer()
    
    # Adjust for ambient noise (crucial for accuracy)
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        
        # This will record until it hears a pause
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return "API Error"

# --- 2. THE MOUTH (Text to Speech) ---
async def generate_audio_file(text, voice="en-US-AriaNeural"):
    """
    Generates an MP3 file using Microsoft Edge's Free Neural TTS.
    Voices: 'en-US-AriaNeural', 'en-US-GuyNeural', 'en-GB-SoniaNeural', etc.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("response.mp3")

def speak_text(text):
    """
    Wrapper to run the async generation and play the audio.
    """
    # 1. Generate the audio file (Async wrapper)
    asyncio.run(generate_audio_file(text))
    
    # 2. Play the audio file using Pygame (Best for preventing UI lag)
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    
    # Block execution while audio plays so the UI stays in "Speaking" mode
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.music.unload()
    try:
        os.remove("response.mp3")
    except:
        pass