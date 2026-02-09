import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v4.0 UI (Industrial Core).
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",     # Cyan
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
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

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

        /* --- CENTER TEXT --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            color: {c};
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 4px;
            text-shadow: 0 0 15px {c};
            animation: pulse-text 2s ease-in-out infinite;
            background: rgba(0,0,0,0.3); /* Slight contrast backing */
            padding: 5px 10px;
            border-radius: 4px;
        }}

        /* --- SHARED RING STYLES --- */
        .ring {{
            position: absolute;
            border-radius: 50%;
            box-shadow: 0 0 10px {c}20; /* Faint glow */
        }}

        /* --- 1. INNER THICK RING --- */
        .ring-inner {{
            width: 180px; height: 180px;
            border: 6px solid {c};
            opacity: 0.8;
            box-shadow: 0 0 20px {c}60;
        }}

        /* --- 2. THE TURBINE (Vertical Lines Radially Outwards) --- */
        .ring-turbine {{
            width: 260px; height: 260px;
            /* Conic gradient creates the "spokes" */
            background: repeating-conic-gradient(
                from 0deg,
                transparent 0deg 3deg,
                {c} 3deg 5deg,  /* The vertical line */
                transparent 5deg 8deg
            );
            /* Mask center to make it a ring */
            -webkit-mask: radial-gradient(farthest-side, transparent 65%, black 66%);
            mask: radial-gradient(farthest-side, transparent 65%, black 66%);
            
            opacity: 0.6;
            animation: spin 40s linear infinite;
        }}

        /* --- 3. THE SPLIT RECTANGLES (Outer Armor) --- */
        /* Layer A: Clockwise */
        .ring-armor-1 {{
            width: 360px; height: 360px;
            border: 10px solid transparent;
            border-top: 10px solid {c};
            border-bottom: 10px solid {c};
            opacity: 0.7;
            filter: drop-shadow(0 0 5px {c});
            animation: spin 12s linear infinite;
        }}

        /* Layer B: Counter-Clockwise (Creates interference/joining effect) */
        .ring-armor-2 {{
            width: 340px; height: 340px;
            border: 8px solid transparent;
            border-left: 8px solid {c};
            border-right: 8px solid {c};
            opacity: 0.5;
            animation: spin-reverse 9s linear infinite;
        }}

        /* --- 4. OUTER DASHED CONTAINMENT --- */
        .ring-outer {{
            width: 440px; height: 440px;
            border: 2px dashed {c}40;
            animation: spin 60s linear infinite;
        }}

        /* --- STATE MODIFICATIONS --- */
        
        /* LISTENING: Turbine slows, core pulses deep */
        .listening .ring-turbine {{ animation-duration: 60s; opacity: 0.8; }}
        .listening .core-text {{ animation: breathe 2s infinite; color: #fff; text-shadow: 0 0 20px {c}; }}

        /* THINKING: Turbine spins FAST, Armor locks up */
        .thinking .ring-turbine {{ animation: spin 2s linear infinite; opacity: 1; }}
        .thinking .ring-armor-1 {{ animation: spin 1s linear infinite; border-width: 4px; }}
        .thinking .ring-armor-2 {{ animation: spin-reverse 1.5s linear infinite; }}
        
        /* SPEAKING: The whole reactor reacts to audio (simulated bounce) */
        .speaking .reactor {{ animation: bounce 0.15s infinite alternate; }}
        .speaking .ring-inner {{ box-shadow: 0 0 40px {c}; background: {c}10; }}

        /* --- ANIMATIONS --- */
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes pulse-text {{ 0% {{ opacity: 0.8; transform: scale(0.95); }} 50% {{ opacity: 1; transform: scale(1.05); }} 100% {{ opacity: 0.8; transform: scale(0.95); }} }}
        @keyframes breathe {{ 0% {{ letter-spacing: 4px; }} 50% {{ letter-spacing: 8px; }} 100% {{ letter-spacing: 4px; }} }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.03); }} }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring ring-outer"></div>

            <div class="ring ring-armor-1"></div>
            <div class="ring ring-armor-2"></div>

            <div class="ring ring-turbine"></div>

            <div class="ring ring-inner"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)