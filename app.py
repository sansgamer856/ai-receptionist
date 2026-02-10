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

# --- CSS MAGIC (The Fix) ---
st.markdown("""
<style>
    /* --- 1. FIX THE CUTOFF & BOXINESS --- */
    
    /* Target the container of the audio widget */
    [data-testid="stAudioInput"] {
        background: transparent !important; /* Remove dark background */
        border: none !important;            /* Remove border */
        box-shadow: none !important;        /* Remove shadow */
        overflow: visible !important;       /* LET THE GLOW SHINE! */
        margin: 0 auto !important;
        width: 80px !important;
        height: 80px !important;
    }

    /* Remove the internal spacing/padding Streamlit adds */
    [data-testid="stAudioInput"] > div {
        background: transparent !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    /* Hide the waveform canvas, timer, and labels */
    [data-testid="stAudioInput"] canvas,
    [data-testid="stAudioInput"] div[data-testid="stMarkdownContainer"],
    [data-testid="stAudioInput"] div[data-testid="stWidgetLabel"] {
        display: none !important;
    }
    
    /* Hide the trash/secondary buttons */
    [data-testid="stAudioInput"] button[kind="secondary"],
    [data-testid="stAudioInput"] button[kind="tertiary"] {
        display: none !important;
    }

    /* --- 2. STYLE THE MIC BUTTON --- */
    
    /* The actual clickable circle */
    [data-testid="stAudioInput"] button[kind="primary"] {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background: rgba(30, 30, 30, 0.8) !important; /* Dark Glass */
        border: 1px solid #333 !important;
        color: #888 !important; /* Dim icon color */
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: all 0.2s ease;
    }

    /* Hover State */
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        border-color: #00f3ff !important;
        color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
        transform: scale(1.05);
    }

    /* --- 3. THE "ACTION AT A DISTANCE" (Make Ball Purple on Press) --- */
    
    /* This uses the :has() selector.
       Logic: "If the Body contains an Active Audio Button, 
       find the Reactor Ring-1 and turn it Purple."
    */
    body:has([data-testid="stAudioInput"] button:active) .reactor .ring-1,
    body:has([data-testid="stAudioInput"] button:focus) .reactor .ring-1 {
        border-color: #d600ff !important;
        box-shadow: 0 0 40px #d600ff !important;
        transform: scale(1.1) rotate(180deg) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Also turn the text purple */
    body:has([data-testid="stAudioInput"] button:active) .core-text {
        color: #d600ff !important;
        text-shadow: 0 0 15px #d600ff !important;
    }

    /* Hide Header/Footer */
    header, footer { visibility: hidden; }
    
</style>
""", unsafe_allow_html=True)

# --- ROBUST AUDIO PLAYER (Base64 Embed) ---
def autoplay_audio(audio_data):
    """
    Embeds audio directly into the HTML to bypass download prompts.
    """
    try:
        if hasattr(audio_data, 'read'):
            audio_bytes = audio_data.read()
        else:
            audio_bytes = audio_data
            
        b64 = base64.b64encode(audio_bytes).decode()
        unique_id = f"audio_{uuid.uuid4().hex}"
        
        # We use audio/mp3 because EdgeTTS outputs MP3s usually.
        # If your engine outputs WAV, change type="audio/wav"
        md = f"""
            <audio id="{unique_id}" autoplay playsinline style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            <script>
                setTimeout(function() {{
                    var audio = document.getElementById("{unique_id}");
                    if (audio) {{
                        audio.play().catch(e => console.error("Play blocked:", e));
                    }}
                }}, 500);
            </script>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio Error: {e}")

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
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        # render_subtitles(ai_response) # Optional: Toggle if you want text on screen
        
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. IDLE DELAY
    wait_time = len(ai_response) * 0.07
    time.sleep(max(3, wait_time)) 
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- LAYOUT ---

# 1. VISUAL LAYER
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. SPACER (Push the mic down a bit)
st.write("")
st.write("")

# 3. MIC INPUT
# The CSS above ensures this looks like a standalone button, not a box.
audio_value = st.audio_input("Voice Uplink")

# 4. MANUAL OVERRIDE (Hidden Menu)
with st.expander("Manual Override", expanded=False):
    with st.form("manual_entry"):
        text_input = st.text_input("Inject Command")
        submitted = st.form_submit_button("Send")
        
    if submitted and text_input:
        st.session_state.messages.append({"role": "user", "content": text_input})
        process_command(text_input)

# --- LOGIC ---

if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Immediate Feedback
    with placeholder_visual.container():
        render_jarvis_ui("listening")
    
    # Transcribe
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
    else:
        time.sleep(1)
        with placeholder_visual.container():
            render_jarvis_ui("idle")