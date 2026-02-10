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

# --- SURGICAL CSS ---
st.markdown("""
<style>
    /* 1. HIDE THE UGLY BOX (The Wrapper) */
    div[data-testid="stAudioInput"] {
        width: 300px !important; /* Match reactor size */
        height: 300px !important;
        margin: auto;
        margin-top: -330px !important; /* Pull UP to cover reactor */
        position: relative;
        z-index: 999; /* Top layer */
        background: transparent !important;
        border: none !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 2. STYLE THE BUTTON (The Actual Click Target) */
    div[data-testid="stAudioInput"] button {
        width: 150px !important;
        height: 150px !important;
        border-radius: 50% !important;
        /* Make it transparent so we see the reactor, OR give it a glass effect */
        background: rgba(255, 255, 255, 0.05) !important; 
        border: 2px solid rgba(0, 243, 255, 0.3) !important;
        color: transparent !important; /* Hide the microphone icon */
        backdrop-filter: blur(2px);
        transition: all 0.3s ease;
    }

    /* Hover effect */
    div[data-testid="stAudioInput"] button:hover {
        background: rgba(0, 243, 255, 0.1) !important;
        border-color: #00f3ff !important;
        transform: scale(1.05);
        cursor: pointer;
    }

    /* 3. RECORDING STATE (The Red/Stop Button) */
    /* When recording, Streamlit changes the button style. We override it. */
    div[data-testid="stAudioInput"] button:active,
    div[data-testid="stAudioInput"] button[title="Stop recording"] {
        background: rgba(214, 0, 255, 0.2) !important; /* Purple tint */
        border-color: #d600ff !important;
        box-shadow: 0 0 30px #d600ff !important;
    }

    /* 4. KILL THE PLAYER (Crucial Step) */
    /* This hides the waveform canvas and the playback audio element */
    div[data-testid="stAudioInput"] canvas,
    div[data-testid="stAudioInput"] audio {
        display: none !important;
    }
    
    /* Hide the "Trash" or "Clear" button if it appears */
    div[data-testid="stAudioInput"] button[kind="secondary"] {
        display: none !important;
    }

    /* Hide the label */
    label[data-testid="stWidgetLabel"] { display: none; }
    
    /* Hide Header/Footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- INVISIBLE AUDIO RESPONSE PLAYER ---
def autoplay_audio(audio_bytes):
    unique_id = f"audio_{uuid.uuid4().hex}"
    b64 = base64.b64encode(audio_bytes.read()).decode()
    md = f"""
        <audio id="{unique_id}" autoplay playsinline style="display:none;">
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>
        <script>
            setTimeout(function() {{
                var audio = document.getElementById("{unique_id}");
                if (audio) {{
                    audio.play().catch(function(e) {{ console.log(e); }});
                }}
            }}, 500);
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
        ai_response = f"System Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. IDLE
    wait_time = len(ai_response) * 0.08
    time.sleep(max(3, wait_time)) 
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN UI STACK ---

# 1. THE VISUAL (Bottom Layer)
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. THE TRIGGER (Top Layer)
# This widget is now visually hacked to be a transparent circle 
# that sits EXACTLY on top of the reactor.
audio_value = st.audio_input("Voice Uplink") 

# --- TRIGGER LOGIC ---
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Visual Feedback
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
        # Subtle error shake or return to idle
        time.sleep(0.5)
        with placeholder_visual.container():
            render_jarvis_ui("idle")