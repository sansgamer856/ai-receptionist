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
    """
    Executes the command and updates the UI flow.
    """
    
    # 1. STATE: THINKING
    # We use placeholder.container() to clear the previous state and render the new one
    with placeholder.container():
        render_jarvis_ui("thinking")
    
    # 2. RUN BACKEND (The Brain)
    try:
        # Pass full history to Gemini so it remembers context
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"I encountered an error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. GENERATE SPEECH (Server Side)
    # This creates the audio bytes to send to the browser
    audio_bytes = voice_engine.get_audio_response(ai_response)
    
    # 4. STATE: SPEAKING
    # CRITICAL FIX: We render BOTH the Animation AND the Audio inside the container
    with placeholder.container():
        render_jarvis_ui("speaking")
        
        # This audio widget will appear directly BELOW the animation
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
    # Wait for audio to finish (Rough estimate based on text length)
    # Avg reading speed ~15 chars per second. We add a buffer.
    time.sleep(len(ai_response) / 13) 
    
    # 5. STATE: IDLE
    with placeholder.container():
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

# The main dynamic area
placeholder = st.empty()

# Render Initial State
with placeholder.container():
    render_jarvis_ui("idle")

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 1. TEXT INPUT
    with st.form("text_form"):
        text_input = st.text_input("Type Command", placeholder="Or use the microphone below...")
        submit_text = st.form_submit_button("SEND TEXT")

    # 2. AUDIO INPUT (Streamlit 1.40+)
    # This native widget handles recording in the browser
    audio_value = st.audio_input("Microphone Link")

# --- LOGIC FLOW ---

# HANDLE TEXT INPUT
if submit_text and text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    process_command(text_input)

# HANDLE VOICE INPUT
if audio_value and audio_value != st.session_state.last_processed_audio:
    st.session_state.last_processed_audio = audio_value
    
    # Show "Listening" state while we upload/transcribe
    with placeholder.container():
        render_jarvis_ui("listening")
    
    # Save the uploaded file temporarily
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
    
    # Transcribe
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.error("Could not understand audio.")
        time.sleep(2)
        with placeholder.container():
            render_jarvis_ui("idle")

# --- LOGS (Optional, for debugging) ---
with st.expander("System Logs"):
    for msg in st.session_state.messages:
        role = msg['role'].upper()
        content = msg['content']
        st.write(f"**{role}:** {content}")