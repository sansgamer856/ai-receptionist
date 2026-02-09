import streamlit as st
import time
from ui_components import render_jarvis_ui
import voice_engine  # Import our new engine

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN PROCESSOR ---
def run_interaction_sequence(user_text=None, ui_placeholder=None):
    """
    The Master Loop: Controls UI states and Voice Logic.
    """
    
    # 1. GET INPUT (If voice was clicked, we listen now)
    final_input = user_text
    
    if final_input is None:
        # STATE: LISTENING
        with ui_placeholder:
            render_jarvis_ui("listening")
        
        # Real Microphone Activation
        detected_text = voice_engine.listen_to_microphone()
        
        if detected_text:
            final_input = detected_text
        else:
            # If nothing heard, return to idle
            with ui_placeholder:
                render_jarvis_ui("idle")
            return

    # Add user to history
    st.session_state.messages.append({"role": "user", "content": final_input})
    
    # 2. STATE: THINKING
    with ui_placeholder:
        render_jarvis_ui("thinking")
    
    # --- [INSERT YOUR LLM / BRAIN HERE] ---
    # For now, we simulate a brain.
    # In the future, replace this with: response = openai_client.chat(...)
    time.sleep(1.5) # Fake thinking time
    
    ai_response = f"I heard you say: {final_input}. My systems are operating at 100% efficiency."
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # 3. STATE: SPEAKING
    with ui_placeholder:
        render_jarvis_ui("speaking")
        
    # Real Voice Activation (Blocking call - UI stays "Speaking" while audio plays)
    voice_engine.speak_text(ai_response)
    
    # 4. STATE: IDLE
    with ui_placeholder:
        render_jarvis_ui("idle")

# --- UI LAYOUT ---

ui_placeholder = st.empty()

# Render Initial State
with ui_placeholder:
    render_jarvis_ui("idle")

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("interaction_form"):
        text_input = st.text_input("Command Input")
        
        c1, c2 = st.columns(2)
        with c1:
            submit_text = st.form_submit_button("SEND TEXT")
        with c2:
            listen_click = st.form_submit_button("ACTIVATE VOICE")

# --- TRIGGER LOGIC ---

if submit_text and text_input:
    run_interaction_sequence(user_text=text_input, ui_placeholder=ui_placeholder)

if listen_click:
    # Trigger the sequence with NO text (forces listening mode)
    run_interaction_sequence(user_text=None, ui_placeholder=ui_placeholder)

# --- LOGS ---
with st.expander("System Logs"):
    for msg in st.session_state.messages:
        st.write(f"**{msg['role'].upper()}:** {msg['content']}")