import streamlit as st
import time
import os
import google.generativeai as genai
from google.cloud import texttospeech
from streamlit_mic_recorder import mic_recorder
from ui_components import render_jarvis_ui

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core (Google Powered)")

# Initialize Google Gemini
# We use 'gemini-1.5-flash' because it is optimized for speed/latency
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing Google API Key in secrets.toml")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "jarvis_state" not in st.session_state:
    st.session_state.jarvis_state = "idle"
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- GOOGLE ARCHITECTURE FUNCTIONS ---

def gemini_listen_and_think(audio_bytes):
    """
    Direct Audio-to-Intelligence using Gemini 1.5 Multimodality.
    We skip the traditional 'Speech-to-Text' step. Gemini hears the audio directly.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # We construct a prompt with the raw audio data
    # Note: In a production app, we might need to save bytes to a temp file for the upload API,
    # but for simplicity, we treat it as a Blob if the SDK supports your version,
    # otherwise we save a temp file.
    
    # 1. Save temp file for Gemini
    with open("temp_input.wav", "wb") as f:
        f.write(audio_bytes)
        
    # 2. Upload to Gemini File API
    audio_file = genai.upload_file("temp_input.wav")
    
    # 3. Generate Content
    prompt = "Listen to this audio. You are N.A.O.M.I., a helpful AI assistant. Respond briefly and conversationally."
    response = model.generate_content([prompt, audio_file])
    
    return response.text

def google_speak(text_response):
    """
    Converts text to speech using Google Cloud TTS.
    """
    try:
        # Client setup (requires Google Cloud credentials in environment)
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.SynthesisInput(text=text_response)

        # Note: We use a 'Journey' voice or 'Studio' voice for premium quality
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-F", # A very natural Google voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        return response.audio_content

    except Exception as e:
        # Fallback if GCP credentials aren't set up
        st.warning(f"Google Cloud TTS Error (Check Credentials): {e}")
        return None

# --- MAIN LAYOUT ---

# 1. The Dynamic UI Container (The "Face")
ui_placeholder = st.empty()

# Render Current State
with ui_placeholder:
    render_jarvis_ui(st.session_state.jarvis_state)

# 2. The Interaction Zone
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # We use a container to stack the mic button nicely
    st.write("### Voice Interface")
    
    # The Mic Recorder Component
    # When the user stops recording, this returns a dictionary with 'bytes'
    audio_data = mic_recorder(
        start_prompt="Click to Speak",
        stop_prompt="Stop Recording",
        key="recorder",
        format="wav" # Gemini likes wav/mp3
    )

# --- THE LOGIC LOOP ---

# Check if new audio was just captured
if audio_data and audio_data['bytes'] != st.session_state.last_audio:
    st.session_state.last_audio = audio_data['bytes']
    
    # --- PHASE 1: THINKING ---
    st.session_state.jarvis_state = "thinking"
    with ui_placeholder:
        render_jarvis_ui("thinking")
    
    # Call Gemini (Audio -> Text)
    try:
        ai_text = gemini_listen_and_think(audio_data['bytes'])
    except Exception as e:
        ai_text = f"Error connecting to Gemini: {e}"
    
    st.session_state.messages.append({"role": "assistant", "content": ai_text})

    # --- PHASE 2: SPEAKING ---
    st.session_state.jarvis_state = "speaking"
    with ui_placeholder:
        render_jarvis_ui("speaking")

    # Generate Audio (Text -> Audio)
    # If you don't have GCP TTS set up, you can swap this function for a simpler library
    audio_output = google_speak(ai_text)
    
    if audio_output:
        # Autoplay the audio
        st.audio(audio_output, format="audio/mp3", autoplay=True)
        
        # Calculate approximate sleep time based on text length to keep the UI "Speaking"
        # Average reading speed: ~15 chars per second
        sleep_time = len(ai_text) / 15
        time.sleep(sleep_time)

    # --- PHASE 3: IDLE ---
    st.session_state.jarvis_state = "idle"
    with ui_placeholder:
        render_jarvis_ui("idle")
        
    # Force a rerun to update the UI state cleanly
    st.rerun()

# Display Chat History (Optional Debug)
with st.expander("Conversation Logs"):
    for msg in st.session_state.messages:
        st.write(f"**{msg['role']}:** {msg['content']}")