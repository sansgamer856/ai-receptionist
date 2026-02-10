import streamlit as st

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I Reactor with a 'hollow' center 
    where we will inject the microphone button.
    """
    
    colors = {
        "idle": "#00f3ff",      
        "listening": "#d600ff", 
        "thinking": "#ffaa00",  
        "speaking": "#ffffff"   
    }
    
    c = colors.get(state, colors["idle"])
    
    css_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500&display=swap');

        /* MAIN CONTAINER */
        .jarvis-container {{
            position: relative;
            width: 100%;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
            overflow: visible; /* Allow mic button to overlap */
            margin-bottom: 0px;
        }}

        /* REACTOR RINGS */
        .reactor {{
            position: relative;
            width: 300px; 
            height: 300px;
            display: flex;
            justify-content: center;
            align-items: center;
            pointer-events: none; /* Let clicks pass through to the mic button below/above */
        }}

        /* TEXT TITLE (Moved up slightly) */
        .core-text {{
            position: absolute;
            top: -40px;
            width: 100%;
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 18px;
            letter-spacing: 4px;
            color: {c};
            opacity: 0.8;
            text-shadow: 0 0 10px {c};
        }}

        .blob-ring {{
            position: absolute;
            border-radius: 50%;
            transition: all 0.5s ease;
            box-shadow: 0 0 15px {c}40;
        }}

        /* Ring Animations */
        .ring-1 {{ width: 260px; height: 260px; border: 3px solid {c}; animation: spin-1 10s linear infinite; }}
        .ring-2 {{ width: 240px; height: 240px; border: 2px dashed {c}; opacity: 0.5; animation: spin-2 15s linear infinite; }}
        .ring-3 {{ width: 280px; height: 280px; border: 1px solid {c}; opacity: 0.3; animation: pulse 4s ease-in-out infinite; }}

        @keyframes spin-1 {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-2 {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
        @keyframes pulse {{ 0% {{ transform: scale(1); opacity: 0.3; }} 50% {{ transform: scale(1.05); opacity: 0.6; }} 100% {{ transform: scale(1); opacity: 0.3; }} }}

        /* STATE MODIFIERS */
        .reactor.listening .ring-1 {{ border-color: #d600ff; box-shadow: 0 0 30px #d600ff; }}
        .reactor.speaking .blob-ring {{ animation-duration: 2s; }}
        
    </style>
    """

    html_code = f"""
    <div class="jarvis-container">
        <div class="reactor {state}">
            <div class="core-text">N.A.O.M.I.</div>
            <div class="blob-ring ring-1"></div>
            <div class="blob-ring ring-2"></div>
            <div class="blob-ring ring-3"></div>
        </div>
    </div>
    """
    
    st.markdown(css_code + html_code, unsafe_allow_html=True)

def render_subtitles(text):
    if not text: return
    st.markdown(f"""
    <div style="
        text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 20px; 
        color: #fff; background: rgba(0,0,0,0.8); padding: 15px; 
        border-radius: 10px; margin: 20px auto; border-bottom: 2px solid #00f3ff;
        max-width: 80%; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)