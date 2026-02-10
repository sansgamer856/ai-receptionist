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

# --- DEEP CSS INTEGRATION ---
st.markdown("""
<style>
    /* 1. HIDE DEFAULT ELEMENTS */
    header, footer {visibility: hidden;}
    
    /* 2. PHANTOM BUTTON SETUP */
    /* Target the container of the audio input */
    div[data-testid="stAudioInput"] {
        width: 300px !important;    /* Match Reactor Size */
        height: 300px !important;   
        margin: 0 auto !important;
        margin-top: -300px !important; /* PULL IT UP over the reactor */
        position: relative;
        z-index: 999; /* TOP LAYER */
    }

    /* 3. STYLE THE INTERNAL BUTTON (The Click Target) */
    div[data-testid="stAudioInput"] button {
        width: 100% !important;
        height: 100% !important;
        border-radius: 50% !important;
        background: transparent !important; /* See-through */
        border: none !important;
        color: transparent !important; /* Hide icon */
        cursor: pointer;
    }
    
    /* Optional: Add a subtle feedback when hovering the 'ball' */
    div[data-testid="stAudioInput"] button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* 4. HIDE THE UGLY 'RESULT' PLAYER */
    /* Once recorded, Streamlit shows an audio player. We hide it to keep the ball clean. */
    div[data-testid="stAudioInput"] audio {
        display: none !important;
    }
    
    /* Hide the label */
    label[data-testid="stWidgetLabel"] { display: none; }
    
</style>
""", unsafe_allow_html=True)

# --- AUDIO PLAYBACK (No Download Prompts) ---
def autoplay_audio(audio_bytes):
    """
    Injects HTML5 Audio using Base64. 
    Prevents mobile download prompts by playing inline.
    """
    unique_id = f"audio_{uuid.uuid4().hex}"
    b64 = base64.b64encode(audio_bytes.read()).decode()
    
    md = f"""
        <audio id="{unique_id}" autoplay playsinline style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            setTimeout(function() {{
                var audio = document.getElementById("{unique_id}");
                if (audio) {{
                    audio.play().catch(e => console.log("Autoplay blocked: " + e));
                }}
            }}, 200);
        </script>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- PROCESSOR ---
def process_command(user_text):
    
    # 1. THINKING STATE
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. BACKEND PROCESSING
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING STATE
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. IDLE RESET
    # Calculate reading time (approx)
    wait_time = max(3, len(ai_response) * 0.08)
    time.sleep(wait_time) 
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN UI STACK ---

# 1. VISUAL LAYER (The Reactor)
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. INTERACTION LAYER (The Phantom Button)
# This widget is physically located here, but CSS pulls it UP 300px 
# to sit directly on top of the reactor above.
audio_value = st.audio_input("Voice Uplink")

# --- LOGIC TRIGGER ---
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Visual feedback
    with placeholder_visual.container():
        render_jarvis_ui("listening")
        
    # Process Audio
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.warning("No audio detected.")
        time.sleep(1)
        with placeholder_visual.container():
            render_jarvis_ui("idle")