import streamlit as st
import backend  # Imports your logic file

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Personal Receptionist",
    page_icon="🤖",
    layout="centered"
)

# --- HEADER ---
st.title("🤖 Personal Receptionist")
st.caption("Managing your Busy Schedule, Research, and Events.")

# --- SESSION STATE (Memory) ---
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm ready to help. You can ask me to check your schedule, add tasks, or send reminders."}
    ]

# --- MEMORY OPTIMIZATION ---
# Keep only the last 15 messages to save tokens and keep the bot fast
if len(st.session_state.messages) > 15:
    st.session_state.messages = st.session_state.messages[-15:]

# --- DISPLAY CHAT HISTORY ---
# This re-draws the conversation every time the app updates
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & LOGIC ---
# This is the ONLY place input is accepted.
if prompt := st.chat_input("Ex: 'Add a Math Exam on Friday at 2 PM'"):
    
    # 1. Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                # Call the backend with the user input and current history
                response_text = backend.process_message(prompt, st.session_state.messages)
                
                st.markdown(response_text)
                
                # 3. Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_msg = f"⚠️ An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- OPTIONAL SIDEBAR ---
with st.sidebar:
    st.header("Controls")
    if st.button("Clear Memory"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption("v1.0 - Connected to Google Calendar & Sheets")