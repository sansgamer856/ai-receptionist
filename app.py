import streamlit as st
import time
import base64
import uuid
from ui_components import render_jarvis_ui, render_subtitles
import voice_engine
import backend

# --- PAGE CONFIG ---
st.set_page_config(layout="centered", page_title="N.A.O.M.I. Core") # Layout is now Centered

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- CSS HACKS FOR "TOUCH" UI ---
st.markdown("""
<style>
    /* 1. Center the Audio Input and make it look integrated */
    .stAudioInput {
        width: 60% !important;
        margin: 0 auto;
        margin-top: -50px; /* Pulls the mic button UP towards the reactor */
        position: relative;
        z-index: 100;
    }
    
    /* 2. Hide the ugly "Label" of the audio input */
    .stAudioInput label {
        display: none;
    }
    
    /* 3. Style the Record Button (This targets Streamlit's internal classes - may vary) */
    div[data-testid="stAudioInput"] button {
        background-color: #00f3ff20;
        border: 1px solid #00f3ff;
        border-radius: 50%;
        width: 60px;
        height: 60px;
    }
    
    /* 4. Hide standard header/footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- MOBILE AUDIO PLAYER ---
def autoplay_audio(audio_bytes):
    unique_id = f"audio_{uuid.uuid4().hex}"
    b64 = base64.b64encode(audio_bytes.read()).decode()
    md = f"""
        <audio id="{unique_id}" controls autoplay playsinline style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            setTimeout(function() {{
                var audio = document.getElementById("{unique_id}");
                if (audio) {{
                    audio.play().catch(function(error) {{
                        console.log("Autoplay blocked: " + error);
                    }});
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
        ai_response = f"Error: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 3. SPEAKING
    audio_io = voice_engine.get_audio_response(ai_response)
    
    with placeholder_visual.container():
        render_jarvis_ui("speaking")
        render_subtitles(ai_response)
        
        if audio_io:
            autoplay_audio(audio_io)
    
    # 4. WAIT & IDLE
    wait_time = len(ai_response) * 0.08
    time.sleep(max(3, wait_time)) 
    
    with placeholder_visual.container():
        render_jarvis_ui("idle")

# --- MAIN UI STACK ---

# 1. VISUAL CORE
placeholder_visual = st.empty()
with placeholder_visual.container():
    render_jarvis_ui("idle")

# 2. INPUT CORE (Stacked directly below)
# The CSS above pulls this UP so it sits near the reactor
audio_value = st.audio_input("Voice Uplink")

# 3. TEXT FALLBACK (Collapsible)
with st.expander("⌨️ Manual Override"):
    with st.form("text_form"):
        text_input = st.text_input("Command", label_visibility="collapsed")
        submit_text = st.form_submit_button("EXECUTE", use_container_width=True)

# --- LOGIC ---
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