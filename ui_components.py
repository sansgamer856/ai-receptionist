import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v5.0 UI (Precision Edition).
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

        /* --- CENTER TEXT (SHIMMER EFFECT) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 6px;
            
            /* The "Loading" Gradient Mask */
            background: linear-gradient(
                90deg, 
                {c}40 0%, 
                {c} 50%, 
                {c}40 100%
            );
            background-size: 200% auto;
            color: #000; /* Fallback */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 1. INNER TECH RING (JUMPS & HOLES) --- */
        .ring-tech {{
            position: absolute;
            width: 160px; height: 160px;
            border-radius: 50%;
            border: 2px solid transparent;
            
            /* Create "Cuts and Holes" using border styles */
            border-top: 4px dotted {c};
            border-bottom: 4px dotted {c};
            border-left: 2px solid {c};
            border-right: 2px solid {c};
            
            box-shadow: 0 0 15px {c}20;
            
            /* Spin + Jump Animation */
            animation: spin-jump 4s ease-in-out infinite;
        }}

        /* --- 2. THE TURBINE (SIMPLE THIN LINES + PADDING) --- */
        .ring-turbine {{
            position: absolute;
            width: 260px; height: 260px; /* Padding from inner ring */
            border-radius: 50%;
            
            /* Razor thin lines */
            background: repeating-conic-gradient(
                from 0deg,
                transparent 0deg 4deg,
                {c} 4deg 4.2deg,  /* Only 0.2deg thick */
                transparent 4.2deg 10deg
            );
            
            -webkit-mask: radial-gradient(farthest-side, transparent 60%, black 65%);
            mask: radial-gradient(farthest-side, transparent 60%, black 65%);
            
            opacity: 0.5;
            animation: spin 30s linear infinite;
        }}

        /* --- 3. OUTER ARMOR (DIAGONAL CUTS) --- */
        /* By setting different border widths, CSS creates diagonal joints */
        .ring-armor {{
            position: absolute;
            width: 380px; height: 380px; /* Padding from turbine */
            border-radius: 50%;
            
            border-top: 12px solid {c};   /* Thick */
            border-right: 2px solid {c}50; /* Thin */
            border-bottom: 12px solid {c}; /* Thick */
            border-left: 2px solid {c}50;  /* Thin */
            
            filter: drop-shadow(0 0 5px {c});
            animation: spin 15s linear infinite;
        }}

        /* A second armor ring spinning opposite for complexity */
        .ring-armor-2 {{
            position: absolute;
            width: 400px; height: 400px;
            border-radius: 50%;
            
            border-top: 2px solid {c}50;
            border-right: 12px solid {c};
            border-bottom: 2px solid {c}50;
            border-left: 12px solid {c};
            
            opacity: 0.4;
            animation: spin-reverse 20s linear infinite;
        }}

        /* --- ANIMATIONS --- */
        
        /* Shimmer moves the opacity across the letters */
        @keyframes text-shimmer {{
            0% {{ background-position: 200% center; }}
            100% {{ background-position: -200% center; }}
        }}

        /* Spin + Jump (Scale) */
        @keyframes spin-jump {{
            0% {{ transform: rotate(0deg) scale(1); }}
            25% {{ transform: rotate(90deg) scale(1.1); }} /* Jump Up */
            50% {{ transform: rotate(180deg) scale(1); }}
            75% {{ transform: rotate(270deg) scale(1.1); }} /* Jump Up */
            100% {{ transform: rotate(360deg) scale(1); }}
        }}

        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        
        /* State Specifics */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        .thinking .ring-turbine {{ animation-duration: 2s; opacity: 0.8; }}
        
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring-armor-2"></div>
            <div class="ring-armor"></div>

            <div class="ring-turbine"></div>

            <div class="ring-tech"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)