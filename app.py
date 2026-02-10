import streamlit as st
import time
from ui_components import render_jarvis_ui
import voice_engine
import backend

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# --- MAIN PROCESSOR ---
def process_command(user_text):
    # 1. STATE: THINKING
    placeholder.empty()
    with placeholder:
        render_jarvis_ui("thinking")
    
    # 2. RUN BACKEND
    try:
        # Pass history to Gemini
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. GENERATE SPEECH (Server Side)
    audio_bytes = voice_engine.get_audio_response(ai_response)
    
    # 4. STATE: SPEAKING & PLAY AUDIO
    # We use st.audio with autoplay=True. 
    # This sends the audio back to the browser to play.
    with placeholder:
        render_jarvis_ui("speaking")
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
    # Wait roughly for audio to finish (estimated) before going idle
    # (Streamlit can't know exactly when audio finishes playing on client)
    time.sleep(len(ai_response) / 10) 
    
    # 5. STATE: IDLE
    with placeholder:
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

placeholder = st.empty()

# Render Initial State (Only if not currently processing)
with placeholder:
    render_jarvis_ui("idle")

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 1. TEXT INPUT
    with st.form("text_form"):
        text_input = st.text_input("Type Command")
        submit_text = st.form_submit_button("SEND")

    # 2. AUDIO INPUT (The Online Mic)
    # This widget appears in the browser. When you stop recording, it re-runs the app.
    audio_value = st.audio_input("Voice Command")

# --- LOGIC FLOW ---

# HANDLE TEXT
if submit_text and text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    process_command(text_input)

# HANDLE AUDIO
# We check if audio_value exists AND if it's different from the last one we processed
if audio_value and audio_value != st.session_state.last_processed_audio:
    st.session_state.last_processed_audio = audio_value
    
    with placeholder:
        render_jarvis_ui("listening")
    
    # Save the uploaded file temporarily so SpeechRecognition can read it
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
    
    # Transcribe
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.error("Could not understand audio.")

# --- LOGS ---
with st.expander("System Logs"):
    for msg in st.session_state.messages:
        role = msg['role'].upper()
        content = msg['content']
        st.write(f"**{role}:** {content}")