import streamlit as st
import time
# Ensure ui_components.py exists in your repo with the Subtitle/CSS code provided earlier
from ui_components import render_jarvis_ui, render_subtitles 
# Ensure voice_engine.py is the Cloud-Compatible version (File/Bytes based)
import voice_engine
import backend

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- MAIN PROCESSOR ---
def process_command(user_text):
    """
    Executes the command and updates the UI flow:
    Thinking -> Backend -> Speaking (w/ Subtitles) -> Idle
    """
    
    # 1. STATE: THINKING
    # Clear placeholder and show thinking animation
    placeholder.empty()
    with placeholder.container():
        render_jarvis_ui("thinking")
    
    # 2. RUN BACKEND (The Brain)
    try:
        # Pass history for context
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Error: {str(e)}"
        
    # Append response to history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. GENERATE AUDIO (Server Side)
    # voice_engine.get_audio_response must return raw bytes!
    audio_bytes = voice_engine.get_audio_response(ai_response)
    
    # 4. STATE: SPEAKING
    # We render Animation + Subtitles + Audio Player in one container
    with placeholder.container():
        # A. The Animation
        render_jarvis_ui("speaking")
        
        # B. The Subtitles (Cinematic text under ring)
        render_subtitles(ai_response)
        
        # C. The Audio Player 
        # (CSS in ui_components will force this to bottom of screen)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
    # 5. DURATION HOLD
    # Calculate how long to keep the "Speaking" state active
    # (Approx 12 chars/sec + 1s buffer)
    wait_time = (len(ai_response) / 12) + 1
    time.sleep(wait_time)
    
    # 6. STATE: IDLE
    with placeholder.container():
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

# The Main Dynamic Container (Top Center)
placeholder = st.empty()

# Render Initial "Idle" State
with placeholder.container():
    render_jarvis_ui("idle")

# Divider
st.markdown("---")

# Input Controls (Bottom)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # A. Text Input Form
    with st.form("text_form"):
        text_input = st.text_input("Manual Override", placeholder="Type a command...")
        submit_text = st.form_submit_button("SEND")

    # B. Audio Input Widget (Browser Microphone)
    # This widget is native to Streamlit 1.40+ and works online.
    audio_value = st.audio_input("Voice Uplink")

# --- TRIGGER LOGIC ---

# 1. Handle Text Input
if submit_text and text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    process_command(text_input)

# 2. Handle Audio Input
if audio_value and audio_value != st.session_state.last_audio:
    # Update state to prevent infinite rerun loop
    st.session_state.last_audio = audio_value
    
    # Show "Listening" State briefly while we process the file
    with placeholder.container():
        render_jarvis_ui("listening")
    
    # Save the uploaded audio byte stream to a temp file
    # This is required because SpeechRecognition needs a file path
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
    
    # Send file to Speech-to-Text
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        # If we heard something, run the main flow
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.error("Audio signal unclear. Please retry.")
        time.sleep(2)
        with placeholder.container():
            render_jarvis_ui("idle")

# --- SYSTEM LOGS (Hidden in Expander) ---
with st.expander("Neural Logs"):
    for msg in st.session_state.messages:
        role = "AI" if msg['role'] == "assistant" else "USER"
        st.write(f"**{role}:** {msg['content']}")