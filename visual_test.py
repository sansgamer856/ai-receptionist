# visual_test.py
import streamlit as st
from ui_components import render_jarvis_ui

st.set_page_config(page_title="JARVIS Interface", page_icon="🤖", layout="wide")

# Dark Mode Hack for Streamlit
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00e5ff !important; font-family: 'Courier New', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("J.A.R.V.I.S. // VISUAL SYSTEM")

# Manual controls to test the states
col1, col2 = st.columns([3, 1])

with col2:
    st.write("### SYSTEM STATE")
    mode = st.radio("Override Protocol:", ["idle", "listening", "thinking", "speaking"])

with col1:
    # This renders the component with the selected state
    render_jarvis_ui(state=mode)

# Optional: Add some "Debug" text to look cool
st.divider()
st.code(f"""
> SYSTEM DIAGNOSTIC...
> CORE TEMPERATURE: STABLE
> CURRENT MODE: {mode.upper()}
> UPLINK: ACTIVE
""", language="json")