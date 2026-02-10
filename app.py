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
    /* 1. CONTAINER FIXES (Remove the Box) */
    [data-testid="stAudioInput"] {
        width: 70px !important;
        height: 70px !important;
        margin: 0 auto !important;
        background: transparent !important;
        border: none !important;
        overflow: visible !important; /* Fixes the cutoff */
        position: relative;
        z-index: 1000;
    }
    
    [data-testid="stAudioInput"] > div {
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        overflow: visible !important;
    }

    /* 2. HIDE JUNK (Waveform, Trash, Time) */
    [data-testid="stAudioInput"] canvas,
    [data-testid="stAudioInput"] div[data-testid="stMarkdownContainer"],
    [data-testid="stAudioInput"] div[data-testid="stWidgetLabel"],
    [data-testid="stAudioInput"] button[kind="secondary"],
    [data-testid="stAudioInput"] button[kind="tertiary"] {
        display: none !important;
    }

    /* 3. THE BUTTON (Unpressed) */
    [data-testid="stAudioInput"] button[kind="primary"] {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background: rgba(20, 20, 20, 0.9) !important;
        border: 2px solid #333 !important;
        color: #555 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Hover */
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        border-color: #00f3ff !important;
        color: #00f3ff !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
        transform: scale(1.05);
    }

    /* 4. THE MAGIC TOGGLE (Listening State) */
    /* When the microphone is active (recording), Streamlit adds a specific class or state. 
       We capture the 'focus' or 'active' state of the button wrapper. */
    
    [data-testid="stAudioInput"]:focus-within button[kind="primary"] {
        background: rgba(0, 243, 255, 0.1) !important;
        border-color: #00f3ff !important;
        box-shadow: 0 0 30px #00f3ff, inset 0 0 20px #00f3ff !important;
        color: #00f3ff !important;
        animation: pulse-recording 1.5s infinite;
    }

    @keyframes pulse-recording {
        0% { box-shadow: 0 0 10px #00f3ff; }
        50% { box-shadow: 0 0 30px #00f3ff; }
        100% { box-shadow: 0 0 10px #00f3ff; }
    }

    /* 5. REACTOR LINKING */
    /* This makes the REACTOR above turn purple/cyan when you hold the button */
    
    /* LISTENING MODE (Cyan) - Triggered by focus/click */
    body:has([data-testid="stAudioInput"]:focus-within) .reactor .core-inner {
        background: #00f3ff !important;
        box-shadow: 0 0 60px #00f3ff !important;
    }
    
    /* HIDE HEADER/FOOTER */
    header, footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- ROBUST AUDIO PLAYER ---
def autoplay_audio(audio_data):
    try:
        if hasattr(audio_data, 'read'):
            audio_bytes = audio_data.read()
        else:
            audio_bytes = audio_data
        b64 = base64.b64encode(audio_bytes).decode()
        unique_id = f"audio_{uuid.uuid4().hex}"
        md = f"""
            <audio id="{unique_id}" autoplay playsinline style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            <script>
                setTimeout(function() {{
                    var audio = document.getElementById("{unique_id}");
                    if (audio) {{ audio.play().catch(e => console.error(e)); }}
                }}, 500);
            </script>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception: pass

# --- PROCESSOR ---
def process_command(user_text):
    
    # 1. THINKING (Triggered immediately after recording stops)
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. BACKEND
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        if audio_io: autoplay_audio(audio_io)
    
    # 4. IDLE
    time.sleep(max(3, len(ai_response) * 0.07))
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- UI STACK ---

# 1. THE REACTOR
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

st.write("") # Spacer

# 2. THE MIC
audio_value = st.audio_input("Voice Uplink")

# 3. MANUAL OVERRIDE (Hidden Menu)
with st.expander("Manual Override"):
    with st.form("manual"):
        txt = st.text_input("Command")
        sub = st.form_submit_button("Send")
    if sub and txt:
        st.session_state.messages.append({"role": "user", "content": txt})
        process_command(txt)

# --- LOGIC ---
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Force 'Thinking' UI immediately since we have the file
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
        
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        with placeholder_visual.container():
            render_jarvis_ui("idle")