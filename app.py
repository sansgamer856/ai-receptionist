import streamlit as st
import backend  # This imports your backend.py file

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Personal Receptionist",
    page_icon="🤖",
    layout="centered"
)

# Custom header styling
st.title("🤖 Personal Receptionist")
st.markdown("*Your AI agent for Google Sheets & Calendar*")

# --- SESSION STATE MANAGEMENT ---
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm connected to your Schedule. specific command would you like me to execute?"}
    ]

# --- DISPLAY CHAT HISTORY ---
# This loop redraws the chat every time the app updates
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT HANDLING ---
if prompt := st.chat_input("Ex: 'Add a Math Exam on Friday at 2 PM'"):
    
    # 1. Display user message immediately in the UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Process with Backend (The "Brain")
    with st.chat_message("assistant"):
        # Show a spinner while Gemini is thinking/calling Google APIs
        with st.spinner("Processing your request..."):
            try:
                # Call the function from backend.py
                response_text = backend.process_message(prompt)
                
                # Display the response
                st.markdown(response_text)
                
                # 3. Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_message = f"⚠️ An error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# --- OPTIONAL: SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption("Connected to: `backend.py`")
    
    # --- MEMORY MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# TOKEN SAVER: Keep only last 15 messages
if len(st.session_state.messages) > 15:
    st.session_state.messages = st.session_state.messages[-15:]

# ... (Display loop same as before) ...

if prompt := st.chat_input("Ex: 'What am I doing tomorrow?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # Pass history (optional, currently backend manages single turn with context)
            response = backend.process_message(prompt, st.session_state.messages)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})