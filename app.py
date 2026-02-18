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
    /* 1. DARK THEME & CHAT LOG STYLING */
    .stApp { background-color: #050505; }
    
    /* Target the Chat Log Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #00f3ff !important;
        border-radius: 10px;
        background: rgba(10, 10, 15, 0.6);
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }

    /* 2. AUDIO INPUT UI CUSTOMIZATION (The Mic) */
    [data-testid="stAudioInput"] {
        width: 70px !important;
        height: 70px !important;
        margin: 0 auto !important;
        margin-top: -30px !important;
        position: relative;
        z-index: 1000;
        overflow: visible !important;
    }
    
    /* Hide the 00:00 timer & junk */
    [data-testid="stAudioInput"] > div:first-child > div:first-child > div:nth-child(2),
    [data-testid="stAudioInput"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stAudioInput"] canvas,
    [data-testid="stAudioInput"] button[kind="secondary"],
    [data-testid="stAudioInput"] button[kind="tertiary"] {
        display: none !important;
    }
    
    /* Style the Primary Button (Mic/Stop) */
    [data-testid="stAudioInput"] button[kind="primary"] {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background: rgba(20, 20, 20, 0.6) !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
        transition: all 0.2s ease;
    }
    [data-testid="stAudioInput"] button[kind="primary"]:hover {
        background: rgba(0, 243, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
        transform: scale(1.05);
    }

    /* 3. THE REAL-TIME "LISTENING" TRIGGER */
    /* When the button title is "Stop recording", the mic is LIVE. */

    body:has(button[title="Stop recording"]) .reactor {
        transform: scale(1.1) !important;
    }
    
    body:has(button[title="Stop recording"]) .blob-ring {
        border-color: #d600ff !important;
        box-shadow: 0 0 50px #d600ff80 !important;
        opacity: 1 !important;
        border-width: 4px !important;
        animation: wobble-1 2s linear infinite !important;
    }
    
    body:has(button[title="Stop recording"]) .core-text {
        background: linear-gradient(90deg, #d600ff 0%, #ff00ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 20px #d600ff !important;
    }
    
    /* Mic button glows purple when recording */
    [data-testid="stAudioInput"] button[title="Stop recording"] {
        border-color: #d600ff !important;
        color: #d600ff !important;
        box-shadow: 0 0 20px #d600ff !important;
        animation: pulse-mic 1.5s infinite;
    }

    @keyframes pulse-mic {
        0% { box-shadow: 0 0 10px #d600ff; }
        50% { box-shadow: 0 0 25px #d600ff; }
        100% { box-shadow: 0 0 10px #d600ff; }
    }

    header, footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


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
    
    # 3. VISUAL: SPEAKING (Green + Subtitles)
    placeholder_visual.empty()
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        
    # 4. AUDIO: NATIVE AUTOPLAY
    audio_io = voice_engine.get_audio_response(ai_response)
    if audio_io:
        st.audio(audio_io, format="audio/mp3", autoplay=True)

    # 5. RETURN TO IDLE
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

# 3. THE MIC INPUT
audio_value = st.audio_input("Voice Uplink")

# 4. THE SYSTEM LOG (Scrollable Native Markdown Container)
st.markdown("### 📝 System Log")
with st.container(height=250, border=True):
    if not st.session_state.messages:
        st.caption("System Initialized. Awaiting Input...")
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<span style='color:#00f3ff; font-weight:bold;'>[USER UPLINK]:</span> {msg['content']}", unsafe_allow_html=True)
        else:
            # AI responses use standard markdown, rendering bullets beautifully
            st.markdown(f"<span style='color:#00ff9d; font-weight:bold;'>[N.A.O.M.I]:</span>\n\n{msg['content']}", unsafe_allow_html=True)
        st.divider()

# 5. THE TEXT INPUT (Native Chat Bar)
# This will lock to the bottom of the screen automatically
text_input = st.chat_input("Message N.A.O.M.I...")


# --- LOGIC CONTROL ---

# Triggered by Text
if text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    st.rerun() # Refresh to show the message in the log instantly, then process
    
# Triggered by Voice
if audio_value and audio_value != st.session_state.last_audio:
    st.session_state.last_audio = audio_value
    
    # Show thinking state
    with placeholder_visual.container():
        render_jarvis_ui("thinking")
        
    with open("temp_input.wav", "wb") as f:
        f.write(audio_value.read())
        
    detected_text = voice_engine.transcribe_audio("temp_input.wav")
    
    if detected_text:
        st.session_state.messages.append({"role": "user", "content": detected_text})
        process_command(detected_text)
        st.rerun() # Refresh to show final log
    else:
        with placeholder_visual.container():
            render_jarvis_ui("idle")

# Process text command if it's pending (happens after st.rerun() from text input)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Ensure it hasn't been processed yet by checking if the last message is from the user
    # (Since process_command appends the AI's response)
    last_msg = st.session_state.messages[-1]["content"]
    process_command(last_msg)
    st.rerun() # Final refresh to show AI's response in the log