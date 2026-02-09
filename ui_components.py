import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v6.0 UI (Heavy Armor Edition).
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
            height: 650px; /* Increased height for larger armor */
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

        /* --- 0. CORE TEXT (PADDED & SHIMMERING) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 32px; /* Larger */
            font-weight: 900;
            letter-spacing: 8px;
            
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 1. THE CONSTANT TURBINE (THICKER & FLOATING) --- */
        .ring-turbine {{
            position: absolute;
            width: 320px; height: 320px; /* Large padding from text */
            border-radius: 50%;
            
            /* THICKER LINES (1.5deg) */
            background: repeating-conic-gradient(
                from 0deg,
                transparent 0deg 5deg,
                {c} 5deg 6.5deg, 
                transparent 6.5deg 10deg
            );
            
            /* MASK: Cuts the center (padding) and outer edge (floating) */
            -webkit-mask: radial-gradient(farthest-side, transparent 65%, black 66%, black 90%, transparent 91%);
            mask: radial-gradient(farthest-side, transparent 65%, black 66%, black 90%, transparent 91%);
            
            opacity: 0.6;
            /* CONSTANT SPEED: Does not change with state */
            animation: spin 60s linear infinite; 
        }}

        /* --- 2. HEXAGONAL CAGE (SHARP ARMOR) --- */
        /* This creates the sharp, non-round look */
        .ring-hex {{
            position: absolute;
            width: 450px; height: 450px;
            border: 2px solid {c};
            opacity: 0.3;
            
            /* Clip path creates a Hexagon */
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            
            animation: spin 30s linear infinite;
        }}

        /* --- 3. HEAVY PLATING (THICK BLOCKS) --- */
        .ring-plate {{
            position: absolute;
            width: 480px; height: 480px;
            border-radius: 50%;
            
            /* Hard stops create "Blocky" look */
            border: 20px solid transparent; 
            border-top: 20px solid {c};
            border-bottom: 20px solid {c};
            
            filter: drop-shadow(0 0 10px {c});
            opacity: 0.8;
            
            animation: spin 15s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
        }}

        /* --- 4. OUTER RETICLE (THIN & SHARP) --- */
        .ring-reticle {{
            position: absolute;
            width: 540px; height: 540px;
            border-radius: 50%;
            border: 1px solid {c}50;
            
            /* Corner cuts */
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            
            animation: spin-reverse 40s linear infinite;
        }}

        /* --- 5. INNER JUMP RING (SMALL & FAST) --- */
        .ring-inner {{
            position: absolute;
            width: 220px; height: 220px;
            border-radius: 50%;
            border-top: 2px solid {c};
            border-bottom: 2px solid {c};
            opacity: 0.5;
            animation: spin-jump 3s ease-in-out infinite;
        }}

        /* --- ANIMATIONS --- */
        @keyframes text-shimmer {{ 0% {{ background-position: 200% center; }} 100% {{ background-position: -200% center; }} }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        
        @keyframes spin-jump {{
            0% {{ transform: rotate(0deg) scale(1); }}
            50% {{ transform: rotate(180deg) scale(1.1); }}
            100% {{ transform: rotate(360deg) scale(1); }}
        }}
        
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

        /* --- STATE LOGIC --- */
        
        /* Thinking: Armor spins fast, Hexagon pulses, Turbine stays CONSTANT */
        .thinking .ring-plate {{ animation: spin 2s linear infinite; border-width: 10px; }}
        .thinking .ring-hex {{ border-width: 5px; opacity: 0.8; animation-duration: 5s; }}
        
        /* Speaking: Bounce effect */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        
        /* Listening: Hexagon expands */
        .listening .ring-hex {{ transform: scale(1.1); transition: transform 0.5s; }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring-reticle"></div>

            <div class="ring-plate"></div>

            <div class="ring-hex"></div>

            <div class="ring-turbine"></div>

            <div class="ring-inner"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=650)