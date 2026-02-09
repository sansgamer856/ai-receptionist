import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v7.0 UI (Machined Tech Edition).
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
            width: 600px;
            height: 600px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* --- 1. THE TITLE (UNTOUCHED) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 8px;
            
            /* The "Glisten" Gradient */
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 2. THE THICK TECH RING (WITH EXTRUSIONS) --- */
        .tech-ring-container {{
            position: absolute;
            width: 300px; height: 300px; /* Padding around text */
            display: flex;
            justify-content: center;
            align-items: center;
            
            /* The "Random" Movement Animation */
            animation: variable-spin-1 20s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
        }}
        
        /* The Base Solid Ring */
        .tech-ring-base {{
            position: absolute;
            width: 100%; height: 100%;
            border-radius: 50%;
            border: 12px solid {c}; /* Thick Solid Line */
            box-shadow: 0 0 20px {c}40;
            opacity: 0.8;
        }}

        /* The Extrusions (Tech Teeth) */
        /* We use a conic gradient to paint "blocks" on top of the border */
        .tech-ring-extrusions {{
            position: absolute;
            width: 340px; height: 340px; /* Slightly larger than base to "extrude" */
            border-radius: 50%;
            
            background: conic-gradient(
                transparent 0deg 10deg,
                {c} 10deg 25deg,       /* Block 1 */
                transparent 25deg 50deg,
                {c} 50deg 55deg,       /* Small Block */
                transparent 55deg 120deg,
                {c} 120deg 160deg,     /* Large Block */
                transparent 160deg 240deg,
                {c} 240deg 250deg,     /* Small Block */
                transparent 250deg 300deg,
                {c} 300deg 330deg,     /* Medium Block */
                transparent 330deg 360deg
            );
            
            /* Mask center to turn the pie chart into a ring of blocks */
            -webkit-mask: radial-gradient(farthest-side, transparent 60%, black 61%);
            mask: radial-gradient(farthest-side, transparent 60%, black 61%);
            
            opacity: 0.8;
        }}

        /* --- 3. THE THIN OUTER LINE --- */
        .outer-ring-container {{
            position: absolute;
            width: 380px; height: 380px;
            
            /* Different Speed/Direction Logic */
            animation: variable-spin-2 25s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
        }}

        .outer-line {{
            width: 100%; height: 100%;
            border-radius: 50%;
            border: 2px solid {c}80; /* Thin Solid Line */
            
            /* Add a small gap to make it look technical */
            border-left: 2px solid transparent;
            transform: rotate(45deg);
        }}

        /* --- ANIMATIONS --- */
        @keyframes text-shimmer {{ 0% {{ background-position: 200% center; }} 100% {{ background-position: -200% center; }} }}

        /* COMPLEX RANDOM MOVEMENT SIMULATION 1 */
        @keyframes variable-spin-1 {{
            0% {{ transform: rotate(0deg); }}
            20% {{ transform: rotate(120deg); }}    /* Fast Forward */
            40% {{ transform: rotate(100deg); }}    /* Slow Reverse */
            50% {{ transform: rotate(100deg); }}    /* Pause */
            70% {{ transform: rotate(260deg); }}    /* Fast Forward */
            85% {{ transform: rotate(240deg); }}    /* Slow Reverse */
            100% {{ transform: rotate(360deg); }}   /* Finish Loop */
        }}

        /* COMPLEX RANDOM MOVEMENT SIMULATION 2 (Offset) */
        @keyframes variable-spin-2 {{
            0% {{ transform: rotate(0deg); }}
            30% {{ transform: rotate(-80deg); }}    /* Reverse */
            50% {{ transform: rotate(-60deg); }}    /* Slow Forward */
            60% {{ transform: rotate(-60deg); }}    /* Pause */
            90% {{ transform: rotate(100deg); }}    /* Fast Forward */
            100% {{ transform: rotate(0deg); }}     /* Back to start */
        }}
        
        /* Thinking Override: Smooth Fast Spin */
        @keyframes spin-fast {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-fast-reverse {{ 100% {{ transform: rotate(-360deg); }} }}

        /* --- STATE LOGIC --- */
        
        /* THINKING: Override random motion with high-speed processing spin */
        .thinking .tech-ring-container {{ animation: spin-fast 1s linear infinite; }}
        .thinking .outer-ring-container {{ animation: spin-fast-reverse 2s linear infinite; }}
        
        /* SPEAKING: Audio Bounce */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

        /* LISTENING: Slow down slightly */
        .listening .tech-ring-container {{ animation-duration: 30s; }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="outer-ring-container">
                <div class="outer-line"></div>
            </div>

            <div class="tech-ring-container">
                <div class="tech-ring-base"></div>
                <div class="tech-ring-extrusions"></div>
            </div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)