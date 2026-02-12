import streamlit as st
import time
import base64
import uuid
from ui_components import render_jarvis_ui
import voice_engine
import backend

# --- PAGE CONFIG ---
st.set_page_config(layout="centered", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- CSS ARCHITECTURE ---
st.markdown("""
<style>
    /* 1. FORCE DARK THEME BACKGROUND */
    .stApp {
        background-color: #050505;
    }

    /* 2. SYSTEM LOG STYLING */
    .system-log-container {
        background: rgba(10, 10, 15, 0.9);
        border: 1px solid #333;
        border-left: 2px solid #00f3ff;
        border-radius: 5px;
        padding: 15px;
        margin-top: 20px;
        height: 200px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .log-entry {
        margin-bottom: 8px;
        border-bottom: 1px dashed #222;
        padding-bottom: 4px;
    }
    .log-user { color: #00f3ff; } /* Cyan */
    .log-ai { color: #00ff9d; }   /* Green */
    .log-time { color: #555; font-size: 10px; margin-right: 8px; }

    /* 3. AUDIO INPUT UI CUSTOMIZATION */
    [data-testid="stAudioInput"] {
        width: 100% !important; /* Full width as requested */
        margin-top: 20px !important;
    }
    
    /* Style the Primary Button (Mic/Stop) */
    [data-testid="stAudioInput"] button[kind="primary"] {
        background: #1a1a1a !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
        transition: all 0.2s ease;
    }
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        background: rgba(0, 243, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
    }

    /* 4. THE REAL-TIME "LISTENING" TRIGGER */
    /* When the button title is "Stop recording", it means the mic is LIVE.
       We use this to OVERRIDE the Reactor CSS to the 'Listening' state.
    */

    /* A. Scale Reactor */
    body:has(button[title="Stop recording"]) .reactor {
        transform: scale(1.1) !important;
    }
    
    /* B. Force Neon Purple Rings (#d600ff) */
    body:has(button[title="Stop recording"]) .blob-ring {
        border-color: #d600ff !important;
        box-shadow: 0 0 50px #d600ff80 !important;
        opacity: 1 !important;
        border-width: 4px !important;
        animation: wobble-1 2s linear infinite !important; /* Faster spin */
    }
    
    /* C. Force Purple Text */
    body:has(button[title="Stop recording"]) .core-text {
        background: linear-gradient(90deg, #d600ff 0%, #ff00ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 20px #d600ff !important;
    }

    /* Hide standard header/footer */
    header, footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- SYSTEM LOG COMPONENT ---
def render_system_log():
    """Renders the chat history as a system log."""
    log_html = '<div class="system-log-container">'
    
    if not st.session_state.messages:
        log_html += '<div class="log-entry"><span class="log-time">SYS</span> <span style="color:#666">System Initialized. Awaiting Input...</span></div>'
    
    for msg in reversed(st.session_state.messages): # Show newest first
        role_class = "log-user" if msg["role"] == "user" else "log-ai"
        role_label = "USER_UPLINK" if msg["role"] == "user" else "CORE_SYSTEM"
        timestamp = time.strftime("%H:%M:%S")
        
        log_html += f"""
        <div class="log-entry">
            <span class="log-time">[{timestamp}]</span>
            <span class="{role_class}">[{role_label}]:</span> 
            <span style="color: #ddd;">{msg["content"]}</span>
        </div>
        """
    
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)

# --- MAIN PROCESSOR ---
def process_command(user_text):
    
    # 1. VISUAL: THINKING (Amber)
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. LOGIC: BACKEND
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. VISUAL: SPEAKING (Green)
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
    
    # 4. AUDIO: NATIVE AUTOPLAY (Reliable)
    audio_io = voice_engine.get_audio_response(ai_response)
    if audio_io:
        # Use native Streamlit audio with autoplay=True (Requires Streamlit 1.29+)
        st.audio(audio_io, format="audio/mp3", autoplay=True)

    # 5. RETURN TO IDLE (After a delay)
    time.sleep(max(3, len(ai_response) * 0.07))
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- UI LAYOUT STACK ---

# 1. THE REACTOR (Visual Core)
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. SPACER
st.write("")

# 3. FULL MIC UI (Visible, not hidden)
# The CSS above ensures the "Recording" state triggers the Reactor changes.
audio_value = st.audio_input("Voice Command Uplink")

# 4. SYSTEM LOG (Chat History)
# We use an empty placeholder so we can update it dynamically if needed
log_placeholder = st.empty()
with log_placeholder.container():
    render_system_log()

# --- LOGIC CONTROL ---
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Immediate 'Thinking' Feedback
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
        
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        
        # Update Log Immediately to show User Input
        with log_placeholder.container():
            render_system_log()
            
        process_command(detected_text)
        
        # Update Log Final (to show AI response)
        with log_placeholder.container():
            render_system_log()
    else:
        with placeholder_visual.container():
            render_jarvis_ui("idle")