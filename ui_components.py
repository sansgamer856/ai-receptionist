import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v3.1 UI (Fixed Core & Positioning).
    """
    
    # --- COLOR PALETTE ---
    # We define the main color, but 'speaking' will get special CSS overrides for the mix.
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#ffffff"   # White (Base) -> Blue added via CSS
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
            /* Push up slightly to make room for text */
            transform: translateY(-20px); 
        }}

        /* --- RINGS --- */
        .ring {{
            position: absolute;
            border-radius: 50%;
            box-shadow: 0 0 10px {main_color}40;
            transition: all 0.5s ease;
            z-index: 1;
        }}

        .ring-1 {{ /* Outer Static */
            width: 380px; height: 380px;
            border: 1px solid {main_color}30;
            box-shadow: none;
        }}

        .ring-2 {{ /* Ticks */
            width: 340px; height: 340px;
            border-left: 4px solid {main_color};
            border-right: 4px solid {main_color};
            border-top: 2px solid transparent;
            border-bottom: 2px solid transparent;
            animation: spin 20s linear infinite;
        }}

        .ring-3 {{ /* Thin Gyro */
            width: 280px; height: 280px;
            border: 1px dashed {main_color}90;
            animation: spin-reverse 25s linear infinite;
        }}

        .ring-4 {{ /* Thick Tech Arcs */
            width: 220px; height: 220px;
            border: 4px solid transparent;
            border-top: 6px solid {main_color};
            border-bottom: 6px solid {main_color};
            filter: drop-shadow(0 0 8px {main_color});
            animation: spin 6s linear infinite;
        }}

        .ring-5 {{ /* Inner Data */
            width: 160px; height: 160px;
            border: 2px dotted {main_color};
            animation: spin-reverse 10s linear infinite;
        }}

        /* --- THE DELTA CORE (Fixed Visibility) --- */
        .triangle-wrapper {{
            position: absolute;
            z-index: 10; /* Ensure it's on top */
            display: flex;
            justify-content: center;
            align-items: center;
            animation: pulse-core 3s ease-in-out infinite;
        }}

        /* The Main Solid Triangle */
        .triangle {{
            width: 80px;
            height: 70px;
            background: {main_color}20; /* 20% opacity fill */
            border: 2px solid {main_color};
            /* Modern clip-path for perfect triangle shape */
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            box-shadow: 0 0 30px {main_color};
        }}

        /* The Inner Glowing Triangle */
        .triangle::after {{
            content: '';
            position: absolute;
            top: 20%; left: 25%;
            width: 50%; height: 50%;
            background: {main_color};
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            box-shadow: 0 0 15px {main_color};
        }}

        /* The Outer Spinning "Star" Triangle */
        .triangle-inverted {{
            position: absolute;
            width: 100px; height: 90px;
            background: transparent;
            border: 1px solid {main_color};
            clip-path: polygon(50% 100%, 0% 0%, 100% 0%); /* Inverted */
            opacity: 0.6;
            animation: spin 12s linear infinite;
        }}

        /* --- TEXT LABEL (Lowered) --- */
        .label {{
            position: absolute;
            bottom: -60px; /* Moved way down */
            color: {main_color};
            letter-spacing: 6px;
            font-size: 16px;
            font-weight: bold;
            text-shadow: 0 0 10px {main_color};
            opacity: 0.9;
        }}

        /* --- SPECIAL SPEAKING STATE (White + Blue Mix) --- */
        /* Overrides the default white to add blue glow */
        .speaking .ring {{ border-color: #ffffff; box-shadow: 0 0 10px #00f3ff; }}
        .speaking .ring-4 {{ border-top-color: #ffffff; border-bottom-color: #ffffff; filter: drop-shadow(0 0 10px #00f3ff); }}
        .speaking .triangle {{ border-color: #ffffff; background: rgba(0, 243, 255, 0.3); box-shadow: 0 0 40px #00f3ff; }}
        .speaking .triangle::after {{ background: #ffffff; box-shadow: 0 0 20px #00f3ff; }}
        .speaking .label {{ color: #ffffff; text-shadow: 0 0 10px #00f3ff; }}
        
        /* Speaking Animation: Bounce */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}

        /* --- OTHER ANIMATIONS --- */
        .listening .triangle-wrapper {{ animation: breathe 2s infinite ease-in-out; }}
        .thinking .ring-2 {{ animation: spin 0.8s linear infinite; border-width: 4px; border-color: #ffaa00; }}
        .thinking .triangle {{ animation: spin-core 1s linear infinite; }}

        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes spin-core {{ 100% {{ transform: rotateY(360deg); }} }}
        @keyframes pulse-core {{ 0% {{ transform: scale(0.9); opacity: 0.8; }} 50% {{ transform: scale(1.05); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.8; }} }}
        @keyframes breathe {{ 0% {{ transform: scale(0.95); }} 50% {{ transform: scale(1.1); }} 100% {{ transform: scale(0.95); }} }}
        @keyframes bounce {{ 0% {{ transform: translateY(-20px) scale(1); }} 100% {{ transform: translateY(-20px) scale(1.02); }} }}

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