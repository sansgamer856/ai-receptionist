import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v14.0 UI (The Perfect Chase).
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

        /* --- TITLE --- */
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

        /* --- 0. BACKGROUND TRACER --- */
        .svg-bg-tracer {{
            position: absolute;
            width: 480px; height: 480px;
            z-index: 0;
            animation: spin-slow 30s linear infinite;
        }}
        .tracer-path-bg {{
            fill: none;
            stroke: {c};
            stroke-width: 1;
            stroke-dasharray: 1445; 
            stroke-dashoffset: 1445;
            opacity: 0.3;
            animation: trace-circle 6s ease-in-out infinite;
        }}

        /* --- 1. THE INFINITY TRACER (SEAMLESS CHASE) --- */
        .svg-complex-tracer {{
            position: absolute;
            width: 380px; height: 380px;
            z-index: 5;
            /* Rotate the container slowly for dynamic angle */
            animation: spin-slow 20s linear infinite;
        }}

        /* THE CHASE LOGIC:
           Path Length ~1400.
           Both animate from 1400 to 0 (one full loop).
           White starts at -0.25s (Ahead).
           Color starts at 0s (Behind).
        */

        /* Trace 1: White Leader (Thin) */
        .trace-white {{
            fill: none;
            stroke: #ffffff;
            stroke-width: 2;
            stroke-linecap: round;
            
            /* Dash = 300, Gap = 1100 (Total 1400) */
            stroke-dasharray: 300 1100;
            
            /* Speed: 3s per loop. Delay: -0.25s (Starts ahead) */
            animation: trace-loop 3s linear infinite;
            animation-delay: -0.25s; 
        }}

        /* Trace 2: Color Follower (Thick) */
        .trace-color {{
            fill: none;
            stroke: {c};
            stroke-width: 6;
            stroke-linecap: square;
            filter: drop-shadow(0 0 10px {c});
            
            /* Dash = 400, Gap = 1000 (Total 1400) */
            stroke-dasharray: 400 1000;
            
            /* Speed: 3s per loop. Delay: 0s (Starts normal) */
            animation: trace-loop 3s linear infinite;
            animation-delay: 0s;
        }}

        /* --- 2. RINGS & ELEMENTS --- */
        .ring-arc {{
            position: absolute;
            width: 240px; height: 240px;
            border-radius: 50%;
            border: 6px solid {c};
            opacity: 0.8;
            -webkit-mask: conic-gradient(from 0deg, transparent 0deg 10deg, black 10deg 110deg, transparent 110deg 130deg, black 130deg 240deg, transparent 240deg 260deg, black 260deg 360deg);
            mask: conic-gradient(from 0deg, transparent 0deg 10deg, black 10deg 110deg, transparent 110deg 130deg, black 130deg 240deg, transparent 240deg 260deg, black 260deg 360deg);
            animation: spin-smooth 20s linear infinite;
        }}

        .ring-scale {{
            position: absolute;
            width: 320px; height: 320px;
            border-radius: 50%;
            background: repeating-conic-gradient(from 0deg, {c} 0deg 0.5deg, transparent 0.5deg 4deg);
            -webkit-mask: radial-gradient(farthest-side, transparent 85%, black 86%);
            mask: radial-gradient(farthest-side, transparent 85%, black 86%);
            opacity: 0.6;
            animation: spin-reverse 40s linear infinite;
        }}

        .ring-cardinal {{
            position: absolute;
            width: 100%; height: 100%;
            pointer-events: none;
        }}

        .cardinal-point {{
            position: absolute;
            left: 50%; top: 50%;
            width: 40px; height: 40px;
            background: {c};
            clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%);
            transform-origin: center center;
            box-shadow: 0 0 15px {c};
        }}
        .north {{ animation: morph-north 6s ease-in-out infinite; }}
        .south {{ animation: morph-south 6s ease-in-out infinite; }}
        .east  {{ animation: morph-east  6s ease-in-out infinite; }}
        .west  {{ animation: morph-west  6s ease-in-out infinite; }}

        .ring-dashed {{
            position: absolute;
            width: 440px; height: 440px;
            border-radius: 50%;
            border: 1px dashed {c};
            opacity: 0.3;
            animation: spin-smooth 60s linear infinite;
        }}

        /* --- ANIMATIONS --- */
        @keyframes spin-smooth {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-slow {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes text-shimmer {{ 0% {{ background-position: 200% center; }} 100% {{ background-position: -200% center; }} }}

        @keyframes trace-circle {{
            0% {{ stroke-dasharray: 0 1445; stroke-dashoffset: 0; }}
            50% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: 0; }}
            100% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: -1445; }}
        }}

        /* THE INFINITY LOOP ANIMATION */
        /* Moves the dash offset by exactly one full path length (1400) */
        @keyframes trace-loop {{
            0% {{ stroke-dashoffset: 1400; }}
            100% {{ stroke-dashoffset: 0; }}
        }}

        @keyframes morph-north {{
            0%, 100% {{ transform: translate(-50%, -200px); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(-50%, -260px); clip-path: polygon(50% 0%, 80% 80%, 50% 60%, 20% 80%); }}
        }}
        @keyframes morph-south {{
            0%, 100% {{ transform: translate(-50%, 160px) rotate(180deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(-50%, 220px) rotate(180deg); clip-path: polygon(50% 0%, 80% 80%, 50% 60%, 20% 80%); }}
        }}
        @keyframes morph-east {{
            0%, 100% {{ transform: translate(160px, -50%) rotate(90deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(220px, -50%) rotate(90deg); clip-path: polygon(50% 0%, 80% 80%, 50% 60%, 20% 80%); }}
        }}
        @keyframes morph-west {{
            0%, 100% {{ transform: translate(-200px, -50%) rotate(-90deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(-260px, -50%) rotate(-90deg); clip-path: polygon(50% 0%, 80% 80%, 50% 60%, 20% 80%); }}
        }}

        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            
            <svg class="svg-bg-tracer" viewBox="0 0 500 500">
                <circle class="tracer-path-bg" cx="250" cy="250" r="230" />
            </svg>

            <svg class="svg-complex-tracer" viewBox="0 0 400 400">
                <defs>
                   <path id="jaggedShape" d="
                     M 200,10 
                     A 190,190 0 0 1 300,40
                     L 280,60 L 320,80
                     A 190,190 0 0 1 380,150
                     L 350,150 L 390,190
                     A 190,190 0 0 1 380,260
                     L 360,250 L 340,290
                     A 190,190 0 0 1 200,390
                     L 200,360 L 180,390
                     A 190,190 0 0 1 50,300
                     L 80,280 L 40,240
                     A 190,190 0 0 1 10,180
                     L 40,180 L 20,130
                     A 190,190 0 0 1 100,40
                     L 110,70 L 140,20
                     Z
                   " />
                </defs>
                
                <use href="#jaggedShape" class="trace-white" />
                
                <use href="#jaggedShape" class="trace-color" />
            </svg>

            <div class="ring-dashed"></div>

            <div class="ring-cardinal">
                <div class="cardinal-point north"></div>
                <div class="cardinal-point south"></div>
                <div class="cardinal-point east"></div>
                <div class="cardinal-point west"></div>
            </div>

            <div class="ring-scale"></div>
            <div class="ring-arc"></div>
            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)