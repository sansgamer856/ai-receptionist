import streamlit as st
import time
import base64
from ui_components import render_jarvis_ui, render_subtitles
import voice_engine
import backend

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- MOBILE AUDIO PLAYER FUNCTION ---
def autoplay_audio(audio_bytes):
    """
    Embeds an HTML5 player with Base64 audio to bypass some mobile restrictions.
    """
    b64 = base64.b64encode(audio_bytes.read()).decode()
    md = f"""
        <audio controls autoplay playsinline style="width: 100%; margin-top: 10px; border-radius: 10px;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.querySelector("audio");
            audio.play().catch(function(error) {{
                console.log("Mobile Autoplay Blocked (User Interaction Required): " + error);
            }});
        </script>
        """
    # We render this inside a specific container so it looks like part of the UI
    st.markdown(md, unsafe_allow_html=True)

# --- PROCESSOR ---
def process_command(user_text):
    
    # 1. THINKING
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. BACKEND
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING
    # Generate Audio Bytes
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        
        # --- NEW MOBILE PLAYER ---
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. WAIT & IDLE
    # Simple calculation: 0.1s per character
    wait_time = len(ai_response) * 0.08
    time.sleep(max(3, wait_time)) # Minimum 3 seconds
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN LAYOUT (SIDE-BY-SIDE) ---
col_visual, col_controls = st.columns([3, 1])

# --- LEFT COLUMN: VISUALS ---
with col_visual:
    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_visual = st.empty()
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- RIGHT COLUMN: CONTROLS ---
with col_controls:
    st.markdown("### 🕹️ Control Deck")
    
    # 1. AUDIO INPUT
    audio_value = st.audio_input("Voice Uplink")
    
    # 2. TEXT INPUT
    with st.form("text_form"):
        text_input = st.text_input("Manual Command", placeholder="Type here...")
        submit_text = st.form_submit_button("EXECUTE", use_container_width=True)

    # 3. LOGS
    with st.expander("📝 System Logs", expanded=False):
        for msg in reversed(st.session_state.messages[-5:]):
            role = "🤖" if msg['role'] == "assistant" else "👤"
            st.caption(f"{role} {msg['content']}")

# --- TRIGGER LOGIC ---
if submit_text and text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    process_command(text_input)

if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    with placeholder_visual.container():
        render_jarvis_ui("listening")
    
    # Save temp file for transcription
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.warning("Signal unclear.")
        time.sleep(1)
        with placeholder_visual.container():
            render_jarvis_ui("idle")