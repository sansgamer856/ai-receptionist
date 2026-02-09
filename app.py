import streamlit as st
import time
from ui_components import render_jarvis_ui
import voice_engine  
import backend  # <--- The Brain (Gemini + Tools)

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="N.A.O.M.I. Core")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN PROCESSOR ---
def run_interaction_sequence(user_text=None, ui_placeholder=None):
    """
    The Master Loop: Listen -> Think (Backend) -> Speak
    """
    
    # 1. GET INPUT
    final_input = user_text
    
    if final_input is None:
        # STATE: LISTENING
        with ui_placeholder:
            render_jarvis_ui("listening")
        
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
    # This is where the magic happens. We call the backend.
    with ui_placeholder:
        render_jarvis_ui("thinking")
    
    try:
        # Call Gemini (with Calendar tools enabled)
        # We pass the full chat history so it remembers context
        ai_response = backend.process_message(final_input, st.session_state.messages)
    except Exception as e:
        ai_response = f"I encountered a critical error in my neural net: {e}"
    
    # Add AI response to history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # 3. STATE: SPEAKING
    with ui_placeholder:
        render_jarvis_ui("speaking")
        
    # Real Voice Activation (Blocks UI while speaking)
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
        text_input = st.text_input("Command Input", placeholder="Ask about your schedule...")
        
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
        role = msg['role'].upper()
        content = msg['content']
        st.write(f"**{role}:** {content}")