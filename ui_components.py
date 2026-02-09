import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v15.0 UI (The Organic Voice Sphere).
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#ffffff"   # White
    }
    
    c = colors.get(state, colors["idle"])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');

        body {{
            background: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 600px;
            overflow: hidden;
            font-family: 'Orbitron', sans-serif;
        }}

        .reactor {{
            position: relative;
            width: 500px;
            height: 500px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* --- TITLE (PRESERVED) --- */
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
        }}

        /* --- THE ORGANIC RINGS --- */
        
        /* Shared Style for all blob rings */
        .blob-ring {{
            position: absolute;
            border-radius: 50%; /* Starts round */
            box-shadow: 0 0 20px {c}40;
            opacity: 0.8;
            transition: all 0.5s ease;
        }}

        /* Ring 1: Main defined line */
        .ring-1 {{
            width: 300px; height: 300px;
            border: 4px solid {c};
            animation: wobble-1 10s ease-in-out infinite;
        }}

        /* Ring 2: Faint outer echo */
        .ring-2 {{
            width: 320px; height: 320px;
            border: 2px solid {c};
            opacity: 0.4;
            animation: wobble-2 15s ease-in-out infinite;
        }}

        /* Ring 3: Inner fast ripple */
        .ring-3 {{
            width: 280px; height: 280px;
            border: 1px solid {c};
            opacity: 0.6;
            animation: wobble-3 8s ease-in-out infinite;
        }}

        /* --- ANIMATIONS --- */

        /* Wobble Logic:
           We change the 4 corners of the border-radius independently using slash syntax:
           border-radius: TL TR BR BL / TL TR BR BL
        */

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

        /* --- STATE LOGIC --- */
        
        /* SPEAKING: The "Breath" (Scale Up/Down rhythmically) */
        /* Note: We combine the wobble (defined above) with a scale via the CONTAINER or override */
        .speaking .blob-ring {{
            animation-duration: 4s; /* Speed up wobble slightly */
            box-shadow: 0 0 30px {c}; /* Brighter glow */
        }}
        
        /* We apply the breathing scale to the container so we don't override the wobble transform on the rings */
        .speaking .reactor {{
            animation: breath-pulse 4s ease-in-out infinite;
        }}

        @keyframes breath-pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.15); }} /* Breathe In */
            100% {{ transform: scale(1); }}   /* Breathe Out */
        }}

        /* THINKING: Fast chaotic wobble */
        .thinking .blob-ring {{
            animation-duration: 2s;
            border-width: 6px;
        }}

        /* LISTENING: Calm, smooth */
        .listening .blob-ring {{
            animation-duration: 20s;
            opacity: 0.9;
        }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="blob-ring ring-2"></div>
            <div class="blob-ring ring-1"></div>
            <div class="blob-ring ring-3"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)