import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the ADVANCED N.A.O.M.I interface.
    States: 'idle', 'listening', 'thinking', 'speaking'
    """
    
    # --- COLOR PALETTE ---
    # Idle: Cyan/Blue (Stable)
    # Listening: Deep Purple/Pink (Attentive)
    # Thinking: Amber/Gold (Processing High Load)
    # Speaking: Bright White/Blue (Active Output)
    
    colors = {
        "idle": {"primary": "#00f3ff", "secondary": "#0066ff", "shadow": "rgba(0, 243, 255, 0.4)"},
        "listening": {"primary": "#bf00ff", "secondary": "#ff0080", "shadow": "rgba(191, 0, 255, 0.5)"},
        "thinking": {"primary": "#ffaa00", "secondary": "#ff5500", "shadow": "rgba(255, 170, 0, 0.5)"},
        "speaking": {"primary": "#ffffff", "secondary": "#00f3ff", "shadow": "rgba(255, 255, 255, 0.6)"}
    }
    
    c = colors.get(state, colors["idle"])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 500px;
            overflow: hidden;
            font-family: 'Courier New', monospace;
        }}

        .container {{
            position: relative;
            width: 400px;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
            transform: scale(0.8); /* Scale down slightly to fit */
        }}

        /* --- CORE ELEMENTS --- */
        
        /* 1. The Central "Heart" */
        .core {{
            position: absolute;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, {c['primary']} 20%, transparent 70%);
            border-radius: 50%;
            box-shadow: 0 0 50px {c['shadow']};
            z-index: 10;
            animation: pulse-core 2s infinite ease-in-out;
        }}

        /* 2. Inner Spinning Dashes */
        .inner-dashed {{
            position: absolute;
            width: 120px;
            height: 120px;
            border: 2px dashed {c['secondary']};
            border-radius: 50%;
            animation: spin 10s linear infinite;
            opacity: 0.7;
        }}

        /* 3. The "Gyroscope" Rings (Opposing rotations) */
        .ring-middle {{
            position: absolute;
            width: 180px;
            height: 180px;
            border-top: 2px solid {c['primary']};
            border-bottom: 2px solid transparent;
            border-left: 4px solid {c['primary']};
            border-right: 2px solid transparent;
            border-radius: 50%;
            animation: spin-reverse 5s linear infinite;
            box-shadow: 0 0 10px {c['shadow']};
        }}

        .ring-outer-thin {{
            position: absolute;
            width: 240px;
            height: 240px;
            border: 1px solid {c['secondary']};
            border-radius: 50%;
            opacity: 0.3;
            animation: pulse-opacity 4s infinite;
        }}

        /* 4. The "Tech Arcs" (Thick incomplete circles) */
        .tech-arc {{
            position: absolute;
            width: 300px;
            height: 300px;
            border: 4px solid transparent;
            border-top: 4px solid {c['primary']};
            border-bottom: 4px solid {c['primary']};
            border-radius: 50%;
            animation: spin 15s linear infinite;
        }}
        
        /* 5. Static HUD Ticks (The ruler lines around the edge) */
        .hud-ticks {{
            position: absolute;
            width: 360px;
            height: 360px;
            border-radius: 50%;
            background: 
                conic-gradient(
                    from 0deg, 
                    transparent 0deg 4deg, 
                    {c['secondary']} 4deg 5deg, 
                    transparent 5deg 9deg, 
                    {c['secondary']} 9deg 10deg
                );
            background-size: 100% 100%;
            mask: radial-gradient(transparent 65%, black 66%);
            -webkit-mask: radial-gradient(transparent 65%, black 66%);
            opacity: 0.5;
            animation: rotate-tick 60s linear infinite;
        }}

        /* --- STATE SPECIFIC ANIMATIONS --- */
        
        /* LISTENING: Expands, turns purple, moves slowly */
        .listening .core {{ animation: pulse-core 0.5s infinite alternate; }}
        .listening .tech-arc {{ border-color: {c['primary']}; animation-duration: 30s; }}
        .listening .inner-dashed {{ border-style: solid; opacity: 0.9; }}

        /* THINKING: Fast spin, chaotic, bright gold */
        .thinking .inner-dashed {{ animation: spin 0.5s linear infinite; border-width: 4px; }}
        .thinking .ring-middle {{ animation: spin-reverse 1s linear infinite; }}
        .thinking .tech-arc {{ animation: spin 2s linear infinite; border-width: 2px; }}
        .thinking .hud-ticks {{ opacity: 0.8; animation: rotate-tick 2s linear infinite; }}

        /* SPEAKING: Pulsing rings like a subwoofer */
        .speaking .container {{ animation: speak-bounce 0.3s infinite alternate; }}
        .speaking .tech-arc {{ border-color: {c['primary']}; box-shadow: 0 0 20px {c['primary']}; }}
        
        /* --- ANIMATION KEYFRAMES --- */
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
        @keyframes pulse-core {{ 0% {{ transform: scale(0.8); opacity: 0.5; }} 100% {{ transform: scale(1.2); opacity: 1; }} }}
        @keyframes pulse-opacity {{ 0% {{ opacity: 0.1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 0.1; }} }}
        @keyframes rotate-tick {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes speak-bounce {{ 0% {{ transform: scale(0.8); }} 100% {{ transform: scale(0.85); }} }}

    </style>
    </head>
    <body>
        <div class="container {state}">
            <div class="hud-ticks"></div>
            <div class="tech-arc"></div>
            <div class="ring-outer-thin"></div>
            <div class="ring-middle"></div>
            <div class="inner-dashed"></div>
            <div class="core"></div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=500)