import streamlit as st
import time
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
    audio_bytes = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    
    # 4. WAIT & IDLE
    wait_time = (len(ai_response) / 12) + 1
    time.sleep(wait_time)
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN LAYOUT (SIDE-BY-SIDE) ---

# We create two main columns
# Left (3): The Visuals (Reactor)
# Right (1): The Controls (Input & Logs)
col_visual, col_controls = st.columns([3, 1])

# --- LEFT COLUMN: VISUALS ---
with col_visual:
    st.markdown("<br>", unsafe_allow_html=True) # Tiny spacer
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

    # 3. LOGS (Collapsed by default to keep it tight)
    with st.expander("📝 System Logs", expanded=False):
        for msg in reversed(st.session_state.messages[-5:]): # Show last 5
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