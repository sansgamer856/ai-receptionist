import streamlit as st

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v15.3 UI (Stabilized Transitions)
    with integrated support for the Fixed Audio Player.
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#ffffff"   # White
    }
    
    c = colors.get(state, colors["idle"])
    
    css_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500&display=swap');

        /* 1. MAIN CONTAINER */
        .jarvis-container {{
            position: relative;
            width: 100%;
            height: 600px; /* Main canvas height */
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
            overflow: hidden;
            font-family: 'Orbitron', sans-serif;
        }}

        /* 2. THE REACTOR (Wobbly Version) */
        .reactor {{
            position: relative;
            width: 400px;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: transform 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        /* --- TITLE --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 6px;
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 3s linear infinite;
            transition: all 0.6s ease;
        }}

        /* --- ORGANIC RINGS --- */
        .blob-ring {{
            position: absolute;
            border-radius: 50%;
            transition: border-color 0.6s ease, box-shadow 0.6s ease, opacity 0.6s ease, border-width 0.6s ease;
            box-shadow: 0 0 20px {c}40;
        }}

        /* Ring 1: Main Line */
        .ring-1 {{
            width: 300px; height: 300px;
            border: 4px solid {c};
            animation: wobble-1 10s ease-in-out infinite;
        }}

        /* Ring 2: Outer Echo */
        .ring-2 {{
            width: 320px; height: 320px;
            border: 2px solid {c};
            opacity: 0.4;
            animation: wobble-2 15s ease-in-out infinite;
        }}

        /* Ring 3: Inner Ripple */
        .ring-3 {{
            width: 280px; height: 280px;
            border: 1px solid {c};
            opacity: 0.6;
            animation: wobble-3 8s ease-in-out infinite;
        }}

        /* --- KEYFRAMES --- */
        @keyframes wobble-1 {{
            0%, 100% {{ border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; transform: rotate(0deg); }}
            50% {{ border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; transform: rotate(180deg); }}
        }}
        @keyframes wobble-2 {{
            0%, 100% {{ border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%; transform: rotate(0deg); }}
            33% {{ border-radius: 70% 30% 50% 50% / 30% 30% 70% 70%; transform: rotate(120deg); }}
            66% {{ border-radius: 30% 70% 70% 30% / 30% 30% 30% 30%; transform: rotate(240deg); }}
        }}
        @keyframes wobble-3 {{
            0%, 100% {{ border-radius: 40% 60% 60% 40% / 60% 30% 70% 40%; transform: rotate(0deg); }}
            50% {{ border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; transform: rotate(-180deg); }}
        }}
        @keyframes text-shimmer {{ 
            0% {{ background-position: 200% center; }} 
            100% {{ background-position: -200% center; }} 
        }}

        /* --- STATE OVERRIDES --- */
        .reactor.listening {{
            transform: scale(1.05);
        }}
        .reactor.listening .blob-ring {{
            opacity: 0.8;
            box-shadow: 0 0 40px {c}60;
        }}

        .reactor.thinking .blob-ring {{
            animation-duration: 3s; 
            animation-timing-function: cubic-bezier(0.86, 0, 0.07, 1);
            border-width: 5px;
            opacity: 1;
        }}
        
        .reactor.speaking {{
            animation: breath-pulse 3s ease-in-out infinite;
        }}
        
        @keyframes breath-pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.12); }}
            100% {{ transform: scale(1); }}
        }}

        /* --- FIXED BOTTOM AUDIO PLAYER --- */
        .stAudio {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            z-index: 9999;
            background: rgba(10, 10, 10, 0.95);
            border: 1px solid {c};
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
            backdrop-filter: blur(5px);
            padding: 5px;
        }}
    </style>
    """

    html_code = f"""
    <div class="jarvis-container">
        <div class="reactor {state}">
            <div class="blob-ring ring-2"></div>
            <div class="blob-ring ring-1"></div>
            <div class="blob-ring ring-3"></div>
            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </div>
    """
    
    st.markdown(css_code + html_code, unsafe_allow_html=True)

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
        background: rgba(0,0,0,0.7); 
        padding: 20px; 
        border-radius: 12px; 
        max-width: 800px;
        
        /* --- CHANGED HERE: Pushed down to avoid overlap --- */
        margin: 10px auto 40px auto; 
        
        border-left: 4px solid #00f3ff;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        position: relative;
        z-index: 100;
        animation: fadein 1s;
    ">
        {text}
    </div>
    <style>@keyframes fadein {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}</style>
    """, unsafe_allow_html=True)