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

# --- CSS FOR "BALL MIC" INTEGRATION ---
# This CSS is aggressive. It targets the internal structure of the Audio Input widget.
st.markdown("""
<style>
    /* 1. CONTAINER POSITIONING */
    /* Move the whole audio widget UP into the reactor space */
    div[data-testid="stAudioInput"] {
        margin-top: -250px !important; /* Pulls it up significantly */
        position: relative;
        z-index: 999; /* Sit ON TOP of the reactor */
        width: 200px !important; /* Force a small width */
        margin-left: auto;
        margin-right: auto;
    }

    /* 2. THE BUTTON ITSELF */
    /* We make the button huge, round, and transparent-ish so it acts as the 'core' */
    div[data-testid="stAudioInput"] button {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        background-color: rgba(0, 243, 255, 0.1) !important; /* Faint Cyan */
        border: 2px solid #00f3ff !important;
        box-shadow: 0 0 20px #00f3ff !important;
        color: transparent !important; /* Hide the mic icon if possible, or let it sit there */
        transition: all 0.3s ease;
    }

    /* Hover State */
    div[data-testid="stAudioInput"] button:hover {
        background-color: rgba(0, 243, 255, 0.3) !important;
        transform: scale(1.1);
        box-shadow: 0 0 40px #00f3ff !important;
    }

    /* Active/Recording State (Streamlit changes styling when active, we catch generic) */
    div[data-testid="stAudioInput"] button:active {
        border-color: #d600ff !important;
        box-shadow: 0 0 30px #d600ff !important;
    }
    
    /* Hide the label "Voice Uplink" */
    label[data-testid="stWidgetLabel"] {
        display: none;
    }

    /* Hide text input details to keep it clean */
    .stTextInput { display: none; } 
    
</style>
""", unsafe_allow_html=True)

# --- AUDIO PLAYER (NO DOWNLOAD) ---
def autoplay_audio(audio_bytes):
    """
    Embeds audio using Base64 Data URI. 
    This prevents the 'Download' prompt on mobile by forcing inline playback.
    """
    unique_id = f"audio_{uuid.uuid4().hex}"
    
    # Read bytes
    audio_data = audio_bytes.read()
    b64 = base64.b64encode(audio_data).decode()
    
    # HTML5 Audio Tag
    # type="audio/mpeg" is crucial for EdgeTTS (which outputs MP3)
    md = f"""
        <audio id="{unique_id}" autoplay playsinline style="display:none;">
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>
        
        <script>
            // Auto-trigger play
            setTimeout(function() {{
                var audio = document.getElementById("{unique_id}");
                if (audio) {{
                    audio.play().catch(function(e) {{
                        console.log("Autoplay blocked, showing controls: " + e);
                        audio.style.display = "block"; // Show player if autoplay fails
                    }});
                }}
            }}, 300);
        </script>
        """
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
        ai_response = f"Neural Link Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING
    # Generate Audio
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. IDLE DELAY
    wait_time = len(ai_response) * 0.08
    time.sleep(max(3, wait_time)) 
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN LAYOUT ---

# 1. VISUAL LAYER (Background)
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. INTERACTION LAYER (Foreground)
# The CSS pulls this widget UP so it sits directly on top of the visual layer.
# The user "Clicks the ball" -> Actually clicks this widget.
audio_value = st.audio_input("Voice Uplink")

# --- LOGIC ---

# Trigger on Audio
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Update UI to 'Listening' (Though usually Streamlit re-runs after stop)
    with placeholder_visual.container():
        render_jarvis_ui("listening")
    
    # Process
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

# Optional: Hidden Text Input for Debugging (Access via expander if needed)
with st.expander("Debug Access", expanded=False):
    manual_text = st.text_input("Inject Command")
    if st.button("Inject"):
        process_command(manual_text)