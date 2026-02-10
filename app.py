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

# --- MINIMALIST CSS (The Fix) ---
st.markdown("""
<style>
    /* 1. HIDE THE UGLY WAVEFORM BAR */
    /* This targets the canvas and the timer text inside the audio widget */
    [data-testid="stAudioInput"] canvas,
    [data-testid="stAudioInput"] div[data-testid="stMarkdownContainer"],
    [data-testid="stAudioInput"] div[data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* 2. HIDE THE RANDOM UPLOAD/DOWNLOAD BUTTONS */
    /* This removes the 'trash' icon and the secondary menu */
    [data-testid="stAudioInput"] button[kind="secondary"],
    [data-testid="stAudioInput"] button[kind="tertiary"] {
        display: none !important;
    }

    /* 3. STYLE THE MAIN MIC BUTTON */
    /* We make the container compact and centered */
    [data-testid="stAudioInput"] {
        width: 80px !important;
        height: 80px !important;
        margin: 0 auto !important; /* Center it */
        display: block !important;
    }

    /* 4. MAKE THE BUTTON GLOW */
    [data-testid="stAudioInput"] button[kind="primary"] {
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        background: rgba(0, 243, 255, 0.1) !important;
        border: 2px solid #00f3ff !important;
        color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
        transition: all 0.3s ease;
    }

    /* Hover State */
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        background: rgba(0, 243, 255, 0.3) !important;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.6);
        transform: scale(1.05);
    }

    /* ACTIVE RECORDING STATE (This turns it Red/Purple when pressed) */
    [data-testid="stAudioInput"] button[kind="primary"]:active,
    [data-testid="stAudioInput"] button[kind="primary"]:focus {
        background: rgba(214, 0, 255, 0.2) !important;
        border-color: #d600ff !important;
        box-shadow: 0 0 25px #d600ff !important;
    }

    /* Hide the header/footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- ROBUST AUDIO PLAYER (Mobile Fix) ---
def autoplay_audio(audio_data):
    """
    Embeds audio as a Base64 string. 
    This forces the browser to play it as a stream, preventing the 'Download WAV' popup.
    """
    try:
        # If audio_data is a BytesIO object, get bytes. If bytes, use directly.
        if hasattr(audio_data, 'read'):
            audio_bytes = audio_data.read()
        else:
            audio_bytes = audio_data
            
        b64 = base64.b64encode(audio_bytes).decode()
        unique_id = f"audio_{uuid.uuid4().hex}"
        
        # HTML5 Audio with playsinline (crucial for mobile)
        md = f"""
            <audio id="{unique_id}" autoplay playsinline style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            
            <script>
                // Force play command
                setTimeout(function() {{
                    var audio = document.getElementById("{unique_id}");
                    if (audio) {{
                        audio.play().catch(e => console.error("Autoplay blocked:", e));
                    }}
                }}, 500);
            </script>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio Playback Error: {e}")

# --- PROCESSOR ---
def process_command(user_text):
    
    # 1. VISUAL: THINKING
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
    
    # 2. LOGIC: BACKEND
    try:
        ai_response = backend.process_message(user_text, st.session_state.messages)
    except Exception as e:
        ai_response = f"System Failure: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. VISUAL: SPEAKING + AUDIO
    # Fetch audio bytes
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        
        # Play Audio (Invisible Player)
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. IDLE DELAY
    # Calculate wait time based on text length (approx 15 chars/sec + buffer)
    wait_time = len(ai_response) * 0.07 
    time.sleep(max(3, wait_time)) 
    
    # Return to Idle
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

# 1. VISUAL LAYER (The Reactor)
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. SPACER
st.write("") # Small gap

# 3. INPUT LAYER (The Minimal Mic)
# This will now appear as just a single button due to our CSS above.
audio_value = st.audio_input("Voice Uplink")

# --- TRIGGER LOGIC ---

if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # 1. IMMEDIATE FEEDBACK: LISTENING
    # We force the UI to 'listening' immediately to acknowledge the input
    with placeholder_visual.container():
        render_jarvis_ui("listening")
    
    # 2. PROCESS AUDIO
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        st.warning("No voice detected.")
        time.sleep(1)
        with placeholder_visual.container():
            render_jarvis_ui("idle")