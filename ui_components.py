import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v8.0 UI (The Vector HUD).
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

        /* --- TITLE (UNCHANGED) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 8px;
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 1. THE "SPLIT-ARC" RING (INNER) --- */
        /* Thick ring with 3 cuts: Top-Right, Bottom, Top-Left */
        .ring-arc {{
            position: absolute;
            width: 240px; height: 240px;
            border-radius: 50%;
            border: 8px solid {c};
            opacity: 0.8;
            
            /* The Mask creates the "Cuts" in the ring */
            -webkit-mask: conic-gradient(
                from 0deg,
                transparent 0deg 10deg,   /* Cut 1 */
                black 10deg 110deg,       /* Solid Arc */
                transparent 110deg 130deg,/* Cut 2 */
                black 130deg 240deg,      /* Solid Arc */
                transparent 240deg 260deg,/* Cut 3 */
                black 260deg 360deg       /* Solid Arc */
            );
            mask: conic-gradient(from 0deg, transparent 0deg 10deg, black 10deg 110deg, transparent 110deg 130deg, black 130deg 240deg, transparent 240deg 260deg, black 260deg 360deg);
            
            animation: spin-smooth 20s linear infinite;
        }}

        /* --- 2. THE "RULER" SCALE (MIDDLE) --- */
        /* Hundreds of small tick marks */
        .ring-scale {{
            position: absolute;
            width: 320px; height: 320px;
            border-radius: 50%;
            
            /* Create ticks using gradient */
            background: repeating-conic-gradient(
                from 0deg,
                {c} 0deg 0.5deg,    /* Tick (Thin) */
                transparent 0.5deg 4deg /* Gap */
            );
            
            /* Hollow out the center */
            -webkit-mask: radial-gradient(farthest-side, transparent 85%, black 86%);
            mask: radial-gradient(farthest-side, transparent 85%, black 86%);
            
            opacity: 0.6;
            animation: spin-reverse 40s linear infinite;
        }}

        /* --- 3. THE "TARGET" TRIANGLES (CARDINAL POINTS) --- */
        /* 4 Triangles pointing inward */
        .ring-target {{
            position: absolute;
            width: 400px; height: 400px;
            animation: spin-step 10s steps(1) infinite; /* Jumps instead of spins */
        }}
        
        .triangle-marker {{
            position: absolute;
            width: 0; height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-top: 15px solid {c};
            left: 50%; top: 0;
            transform: translateX(-50%);
        }}
        /* Duplicate triangles for other sides using pseudo-elements would be complex, 
           so we use box-shadow or multiple divs. Let's use 4 divs for cleaner code. */

        /* --- 4. THE "CIRCUIT" DASHES (OUTER) --- */
        .ring-dashed {{
            position: absolute;
            width: 440px; height: 440px;
            border-radius: 50%;
            border: 2px dashed {c};
            opacity: 0.4;
            animation: spin-smooth 60s linear infinite;
        }}

        /* --- ANIMATIONS --- */
        @keyframes spin-smooth {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes text-shimmer {{ 0% {{ background-position: 200% center; }} 100% {{ background-position: -200% center; }} }}
        
        @keyframes spin-step {{
            0% {{ transform: rotate(0deg); }}
            25% {{ transform: rotate(90deg); }}
            50% {{ transform: rotate(180deg); }}
            75% {{ transform: rotate(270deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        @keyframes pulse-scale {{ 0% {{ transform: scale(1); opacity: 0.6; }} 50% {{ transform: scale(1.02); opacity: 0.8; }} 100% {{ transform: scale(1); opacity: 0.6; }} }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

        /* --- STATE LOGIC --- */
        .thinking .ring-arc {{ animation: spin-smooth 2s linear infinite; border-width: 4px; }}
        .thinking .ring-scale {{ animation: spin-reverse 4s linear infinite; }}
        
        /* Speaking: Bounce + Color Mix */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        .speaking .ring-arc {{ border-color: #ffffff; box-shadow: 0 0 10px {c}; }}
        
        /* Listening: Scale breathes */
        .listening .ring-scale {{ animation: pulse-scale 2s infinite ease-in-out; }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring-dashed"></div>

            <div class="ring-target">
                <div class="triangle-marker" style="top: 0; transform: translateX(-50%) rotate(0deg);"></div>
                <div class="triangle-marker" style="top: 50%; right: -10px; transform: translateY(-50%) rotate(-90deg); left: auto;"></div>
                <div class="triangle-marker" style="bottom: 0; top: auto; transform: translateX(-50%) rotate(180deg);"></div>
                <div class="triangle-marker" style="top: 50%; left: -10px; transform: translateY(-50%) rotate(90deg);"></div>
            </div>

            <div class="ring-scale"></div>

            <div class="ring-arc"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)