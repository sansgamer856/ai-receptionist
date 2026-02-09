import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v3.0 UI (Triangular Core Edition).
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",     # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#ffffff"   # White
    }
    
    main_color = colors.get(state, colors["idle"])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

        body {{
            background: transparent;
            margin: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 600px;
            overflow: hidden;
            font-family: 'Orbitron', sans-serif;
        }}

        /* --- THE MAIN CONTAINER --- */
        .reactor {{
            position: relative;
            width: 400px;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* --- SHARED RING STYLES --- */
        .ring {{
            position: absolute;
            border-radius: 50%;
            box-shadow: 0 0 10px {main_color}40; /* Low opacity glow */
            transition: all 0.5s ease;
        }}

        /* --- LAYER 1: OUTER STATIC HUD --- */
        .ring-1 {{
            width: 380px; height: 380px;
            border: 1px solid {main_color}20; /* Very faint */
            box-shadow: none;
        }}

        /* --- LAYER 2: ROTATING TICKS --- */
        .ring-2 {{
            width: 340px; height: 340px;
            border-left: 2px solid {main_color};
            border-right: 2px solid {main_color};
            border-top: 2px solid transparent;
            border-bottom: 2px solid transparent;
            animation: spin 15s linear infinite;
        }}

        /* --- LAYER 3: THIN GYRO --- */
        .ring-3 {{
            width: 280px; height: 280px;
            border: 1px dashed {main_color}80;
            animation: spin-reverse 20s linear infinite;
        }}

        /* --- LAYER 4: TECH ARCS (The thick parts) --- */
        .ring-4 {{
            width: 220px; height: 220px;
            border: 4px solid transparent;
            border-top: 4px solid {main_color};
            border-bottom: 4px solid {main_color};
            filter: drop-shadow(0 0 5px {main_color});
            animation: spin 4s linear infinite;
        }}

        /* --- LAYER 5: INNER DATA RING --- */
        .ring-5 {{
            width: 160px; height: 160px;
            border-radius: 50%;
            border: 2px dotted {main_color};
            animation: spin-reverse 8s linear infinite;
        }}

        /* --- THE CORE: TRIANGLE DESIGN --- */
        .triangle-wrapper {{
            position: absolute;
            width: 0; 
            height: 0; 
            display: flex;
            justify-content: center;
            align-items: center;
            animation: pulse-core 2s ease-in-out infinite;
        }}

        .triangle {{
            width: 80px;
            height: 70px;
            background-color: {main_color}10; /* Transparent fill */
            border-bottom: 2px solid {main_color};
            position: relative;
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            box-shadow: 0 0 20px {main_color};
        }}
        
        /* Inner glowing triangle */
        .triangle::after {{
            content: '';
            position: absolute;
            top: 10px; left: 20px;
            width: 40px; height: 35px;
            background: {main_color};
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            box-shadow: 0 0 20px {main_color};
        }}
        
        /* Inverted Triangle for "Star" effect */
        .triangle-inverted {{
            position: absolute;
            width: 80px; height: 70px;
            border-top: 2px solid {main_color};
            background-color: transparent;
            clip-path: polygon(0% 0%, 100% 0%, 50% 100%);
            opacity: 0.5;
            animation: spin 10s linear infinite; /* Spin the outer triangle */
        }}

        /* --- TEXT LABEL --- */
        .label {{
            position: absolute;
            bottom: 20px;
            color: {main_color};
            letter-spacing: 4px;
            font-size: 14px;
            text-shadow: 0 0 10px {main_color};
            opacity: 0.8;
        }}

        /* --- STATE ANIMATIONS --- */
        
        /* LISTENING: Slow, deep breathing */
        .listening .ring-4 {{ animation-duration: 10s; box-shadow: 0 0 15px {main_color}; }}
        .listening .triangle-wrapper {{ animation: breathe 3s infinite ease-in-out; }}

        /* THINKING: Fast, chaotic spin */
        .thinking .ring-2 {{ animation: spin 1s linear infinite; border-width: 4px; }}
        .thinking .ring-4 {{ animation: spin-reverse 1.5s linear infinite; }}
        .thinking .ring-5 {{ border-style: solid; border-width: 2px; }}
        
        /* SPEAKING: Reaction to sound */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        .speaking .triangle {{ background: {main_color}; }} /* Solid core when speaking */

        /* --- KEYFRAMES --- */
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes pulse-core {{ 0% {{ opacity: 0.7; transform: scale(0.95); }} 50% {{ opacity: 1; transform: scale(1.05); }} 100% {{ opacity: 0.7; transform: scale(0.95); }} }}
        @keyframes breathe {{ 0% {{ transform: scale(0.9); }} 50% {{ transform: scale(1.1); }} 100% {{ transform: scale(0.9); }} }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
            <div class="ring ring-4"></div>
            <div class="ring ring-5"></div>
            
            <div class="triangle-wrapper">
                <div class="triangle-inverted"></div>
                <div class="triangle"></div>
            </div>
            
            <div class="label">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)