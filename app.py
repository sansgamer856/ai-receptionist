import streamlit as st
import time
import base64
import uuid
from ui_components import render_jarvis_ui, render_subtitles
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
    /* --- 1. MIC BUTTON POSITIONING --- */
    [data-testid="stAudioInput"] {
        width: 70px !important;
        height: 70px !important;
        margin: 0 auto !important;
        
        /* PULL UP: Move closer to the reactor */
        margin-top: -60px !important; 
        
        background: transparent !important;
        overflow: visible !important;
        position: relative;
        z-index: 1000;
    }
    
    [data-testid="stAudioInput"] > div {
        padding: 0 !important;
        background: transparent !important;
    }

    /* HIDE THE UGLY BARS */
    [data-testid="stAudioInput"] canvas,
    [data-testid="stAudioInput"] div[data-testid="stMarkdownContainer"],
    [data-testid="stAudioInput"] div[data-testid="stWidgetLabel"],
    [data-testid="stAudioInput"] button[kind="secondary"],
    [data-testid="stAudioInput"] button[kind="tertiary"] {
        display: none !important;
    }

    /* --- 2. MIC BUTTON STYLE --- */
    [data-testid="stAudioInput"] button[kind="primary"] {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background: rgba(20, 20, 20, 0.4) !important; /* Subtle glass */
        border: 1px solid #444 !important;
        color: #666 !important; /* Dim icon */
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }

    /* Hover State */
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        border-color: #d600ff !important;
        color: #d600ff !important;
        box-shadow: 0 0 15px #d600ff60;
        transform: scale(1.1);
    }

    /* --- 3. THE "ACTION AT A DISTANCE" (Mic -> Reactor Link) --- */
    
    /* When the Mic is Active/Focused (Pressed): */
    
    /* A. Scale the Reactor Up */
    body:has([data-testid="stAudioInput"]:focus-within) .reactor {
        transform: scale(1.05) !important;
    }
    
    /* B. Turn Rings Neon Purple (#d600ff) */
    body:has([data-testid="stAudioInput"]:focus-within) .blob-ring {
        border-color: #d600ff !important;
        box-shadow: 0 0 40px #d600ff60 !important;
        opacity: 0.9 !important;
        border-width: 3px !important;
    }
    
    /* C. Turn Text Neon Purple */
    body:has([data-testid="stAudioInput"]:focus-within) .core-text {
        color: #d600ff !important;
        text-shadow: 0 0 20px #d600ff !important;
    }

    /* Hide Header/Footer */
    header, footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- ROBUST AUDIO PLAYER ---
def autoplay_audio(audio_data):
    try:
        if hasattr(audio_data, 'read'): audio_bytes = audio_data.read()
        else: audio_bytes = audio_data
        b64 = base64.b64encode(audio_bytes).decode()
        unique_id = f"audio_{uuid.uuid4().hex}"
        
        # Using playsinline for mobile compatibility
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
    
    # 1. VISUAL: THINKING (Gold/Amber)
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. LOGIC: BACKEND
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. VISUAL: SPEAKING (Green/Cyan + Subtitles)
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response) # <--- ENABLED
        if audio_io: autoplay_audio(audio_io)
    
    # 4. IDLE DELAY
    time.sleep(max(3, len(ai_response) * 0.07))
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

# 1. THE REACTOR
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. SPACER (Just a small one)
st.write("") 

# 3. THE MIC
audio_value = st.audio_input("Voice Uplink")

# 4. MANUAL OVERRIDE (Hidden Menu)
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
    
    # Immediate 'Thinking' Feedback (since recording is done)
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
        
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        # Return to idle if no voice found
        with placeholder_visual.container():
            render_jarvis_ui("idle")