import streamlit as st

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I Reactor.
    This acts as the VISUAL LAYER (Background).
    """
    
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Purple
        "thinking": "#ffaa00",  # Gold
        "speaking": "#ffffff"   # White
    }
    
    c = colors.get(state, colors["idle"])
    
    # We use a fixed height container to ensure alignment with the overlay
    css_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');

        /* The Container */
        .reactor-container {{
            position: relative;
            width: 300px;
            height: 300px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1; /* Sits behind the click layer */
        }}

        /* The Core Text */
        .core-text {{
            position: absolute;
            z-index: 5;
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            letter-spacing: 3px;
            color: {c};
            text-shadow: 0 0 10px {c};
            pointer-events: none;
        }}

        /* The Rings */
        .ring {{
            position: absolute;
            border-radius: 50%;
            box-shadow: 0 0 15px {c}40;
            transition: all 0.5s ease;
        }}

        .r1 {{ width: 100%; height: 100%; border: 2px solid {c}; animation: spin1 10s linear infinite; }}
        .r2 {{ width: 80%; height: 80%; border: 1px dashed {c}; opacity: 0.6; animation: spin2 15s linear infinite; }}
        .r3 {{ width: 60%; height: 60%; border: 4px double {c}; opacity: 0.4; animation: pulse 3s ease-in-out infinite; }}

        @keyframes spin1 {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin2 {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
        @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.4; }} 50% {{ transform: scale(1.05); opacity: 0.8; }} 100% {{ transform: scale(0.9); opacity: 0.4; }} }}

        /* State specific tweaks */
        .reactor-container.listening .r1 {{ border-color: #d600ff; box-shadow: 0 0 30px #d600ff; }}
        
    </style>
    """

    html_code = f"""
    <div class="reactor-container {state}">
        <div class="core-text">N.A.O.M.I.</div>
        <div class="ring r1"></div>
        <div class="ring r2"></div>
        <div class="ring r3"></div>
    </div>
    """
    
    st.markdown(css_code + html_code, unsafe_allow_html=True)

def render_subtitles(text):
    if not text: return
    st.markdown(f"""
    <div style="
        text-align: center; font-family: sans-serif; font-size: 18px; 
        color: #fff; background: rgba(0,0,0,0.6); padding: 10px; 
        border-radius: 8px; margin-top: 20px;
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)