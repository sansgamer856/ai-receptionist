# ui_components.py
import streamlit as st

def render_jarvis_ui(state="idle"):
    """
    Renders the animated JARVIS interface based on the state.
    States: 'idle', 'listening', 'thinking', 'speaking'
    """
    
    # Define the colors and animation speeds for each state
    # This CSS handles the "Iron Man" look
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px; /* Height of the visual container */
            overflow: hidden;
        }}

        /* --- THE REACTOR CONTAINER --- */
        .reactor-container {{
            position: relative;
            width: 300px;
            height: 300px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* --- COMMON RING STYLES --- */
        .ring {{
            position: absolute;
            border-radius: 50%;
            border: 2px solid transparent;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3); /* Cyan Glow */
            transition: all 0.5s ease;
        }}

        /* --- OUTER RING --- */
        .outer {{
            width: 280px;
            height: 280px;
            border-top: 4px solid #00e5ff;
            border-bottom: 2px solid #00e5ff;
            animation: spin 10s linear infinite;
        }}

        /* --- MIDDLE RING --- */
        .middle {{
            width: 220px;
            height: 220px;
            border-left: 4px solid #00e5ff;
            border-right: 2px solid #00e5ff;
            animation: spin-reverse 6s linear infinite;
        }}

        /* --- INNER RING --- */
        .inner {{
            width: 150px;
            height: 150px;
            border: 2px dashed #00e5ff;
            animation: spin 4s linear infinite;
        }}

        /* --- CORE (The Dot) --- */
        .core {{
            position: absolute;
            width: 50px;
            height: 50px;
            background-color: #00e5ff;
            border-radius: 50%;
            box-shadow: 0 0 30px #00e5ff, 0 0 60px #00e5ff;
            animation: pulse 2s infinite;
        }}

        /* --- STATE MODIFICATIONS --- */
        
        /* LISTENING: Outer rings slow down, Core pulses wildly */
        .listening .outer {{ animation-duration: 20s; opacity: 0.5; }}
        .listening .middle {{ animation-duration: 15s; opacity: 0.5; }}
        .listening .core {{ animation: pulse-fast 0.5s infinite; background-color: #ff0055; box-shadow: 0 0 30px #ff0055; }}

        /* THINKING: Fast chaotic spinning */
        .thinking .outer {{ animation: spin 1s linear infinite; border-color: #ffcc00; box-shadow: 0 0 20px #ffcc00; }}
        .thinking .middle {{ animation: spin-reverse 1.5s linear infinite; border-color: #ffcc00; }}
        .thinking .core {{ background-color: #ffcc00; box-shadow: 0 0 40px #ffcc00; }}

        /* SPEAKING: The rings expand and contract like a voice */
        .speaking .outer {{ animation: breathe 1s ease-in-out infinite alternate; }}
        .speaking .middle {{ animation: breathe 0.8s ease-in-out infinite alternate-reverse; }}
        .speaking .core {{ width: 60px; height: 60px; }}

        /* --- KEYFRAMES (Animation Logic) --- */
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
        @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.7; }} 50% {{ transform: scale(1.1); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.7; }} }}
        @keyframes pulse-fast {{ 0% {{ transform: scale(0.8); }} 50% {{ transform: scale(1.2); }} 100% {{ transform: scale(0.8); }} }}
        @keyframes breathe {{ 0% {{ transform: scale(1) rotate(0deg); }} 100% {{ transform: scale(1.1) rotate(10deg); }} }}

    </style>
    </head>
    <body>
        <div class="reactor-container {state}">
            <div class="ring outer"></div>
            <div class="ring middle"></div>
            <div class="ring inner"></div>
            <div class="core"></div>
        </div>
    </body>
    </html>
    """
    
    # Inject into Streamlit
    st.components.v1.html(html_code, height=450)