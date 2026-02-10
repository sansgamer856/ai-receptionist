import streamlit as st

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I UI with:
    1. The Central Reactor Animation
    2. A fixed-bottom Audio Player
    3. Cinematic Subtitles
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#00ff41"   # Matrix Green (Changed to differentiate speaking)
    }
    
    c = colors.get(state, colors["idle"])
    
    css_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500&display=swap');

        /* 1. THE CONTAINER */
        .jarvis-container {{
            position: relative;
            width: 100%;
            height: 450px; /* Reduced height to fit subtitles */
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
            overflow: hidden;
        }}

        /* 2. THE REACTOR (Animation) */
        .reactor {{
            position: relative;
            width: 300px;
            height: 300px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
            background: radial-gradient(circle, {c}10 0%, transparent 70%);
            box-shadow: 0 0 50px {c}20;
            transition: all 0.5s ease;
        }}

        .core-circle {{
            width: 120px;
            height: 120px;
            background: {c};
            border-radius: 50%;
            box-shadow: 0 0 60px {c}, inset 0 0 20px rgba(255,255,255,0.8);
            position: relative;
            z-index: 10;
        }}

        .blob-ring {{
            position: absolute;
            width: 100%;
            height: 100%;
            border: 2px solid {c};
            border-radius: 50%;
            box-shadow: 0 0 15px {c};
            opacity: 0.6;
            animation: spin 10s linear infinite;
        }}

        /* ANIMATION STATES */
        .reactor.listening {{ transform: scale(1.1); }}
        .reactor.listening .blob-ring {{ animation-duration: 4s; border-width: 4px; }}
        
        .reactor.thinking .core-circle {{ animation: pulse 0.5s alternate infinite; }}
        
        .reactor.speaking .blob-ring {{ animation: ripple 1.5s infinite; }}

        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes pulse {{ 0% {{ opacity: 0.8; }} 100% {{ opacity: 1; box-shadow: 0 0 80px {c}; }} }}
        @keyframes ripple {{ 0% {{ transform: scale(1); opacity: 0.8; }} 100% {{ transform: scale(1.5); opacity: 0; }} }}

        /* 3. FIXED BOTTOM AUDIO PLAYER */
        /* This targets the Streamlit Audio widget specifically */
        .stAudio {{
            position: fixed;
            bottom: 10px;
            left: 0;
            right: 0;
            width: 80%;
            margin: 0 auto;
            z-index: 999;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid {c};
            backdrop-filter: blur(10px);
        }}
    </style>
    """

    html_code = f"""
    <div class="jarvis-container">
        <div class="reactor {state}">
            <div class="core-circle"></div>
            <div class="blob-ring" style="width: 140%; height: 140%;"></div>
            <div class="blob-ring" style="width: 180%; height: 180%; animation-direction: reverse;"></div>
        </div>
    </div>
    """
    
    # Inject CSS
    st.markdown(css_code, unsafe_allow_html=True)
    
    # Render HTML
    st.markdown(html_code, unsafe_allow_html=True)

def render_subtitles(text):
    """
    Renders cinematic subtitles below the animation.
    """
    if not text:
        return
        
    st.markdown(f"""
    <div style="
        text-align: center; 
        font-family: 'Rajdhani', sans-serif; 
        font-size: 24px; 
        color: #e0e0e0; 
        background: rgba(0,0,0,0.5); 
        padding: 15px; 
        border-radius: 10px; 
        margin-top: -50px; 
        border-left: 4px solid #00f3ff;
        animation: fadein 1s;
    ">
        {text}
    </div>
    <style>@keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}</style>
    """, unsafe_allow_html=True)