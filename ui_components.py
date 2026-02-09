import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v10.0 UI (Shuriken & Dual Tracer).
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

        /* --- TITLE (SLIGHTLY LARGER) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 26px; /* Increased from 20px */
            font-weight: 900;
            letter-spacing: 6px;
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 0. BACKGROUND TRACER (SIMPLE CIRCLE) --- */
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

        /* --- NEW: THE COMPLEX DOUBLE TRACER (BETWEEN RINGS) --- */
        .svg-complex-tracer {{
            position: absolute;
            width: 380px; height: 380px; /* Sits between Scale and Outer */
            z-index: 5;
            /* No rotation on the container, the paths draw the shape */
        }}

        /* The Geometry: A Tech Octagon */
        /* d="M 190,40 L 240,40 L 260,90 L 320,90 L 340,140 ... " (Simplified below) */
        
        /* Trace 1: Thin White Leader */
        .trace-white {{
            fill: none;
            stroke: #ffffff;
            stroke-width: 1;
            stroke-linecap: round;
            stroke-dasharray: 1200; /* Approx length of shape */
            stroke-dashoffset: 1200;
            animation: draw-complex 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }}

        /* Trace 2: Thick Color Laggard */
        .trace-color {{
            fill: none;
            stroke: {c};
            stroke-width: 4; /* Thicker */
            stroke-linecap: square;
            /* Short segment (Comet) */
            stroke-dasharray: 200 1200; 
            stroke-dashoffset: 1200;
            filter: drop-shadow(0 0 5px {c});
            /* Same animation, but slight delay/offset visually handled by dasharray */
            animation: draw-complex 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            animation-delay: 0.1s; /* Slight lag */
        }}

        /* --- 1. THE SPLIT-ARC RING --- */
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

        /* --- 2. THE RULER SCALE --- */
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

        /* --- 3. MORPHING SHURIKENS (Updated Shape) --- */
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
            
            /* Start: Standard Triangle */
            clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%);
            transform-origin: center center;
            box-shadow: 0 0 15px {c};
        }}

        .north {{ animation: morph-north 6s ease-in-out infinite; }}
        .south {{ animation: morph-south 6s ease-in-out infinite; }}
        .east  {{ animation: morph-east  6s ease-in-out infinite; }}
        .west  {{ animation: morph-west  6s ease-in-out infinite; }}

        /* --- 4. OUTER DASHED --- */
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

        /* Simple Circle Trace */
        @keyframes trace-circle {{
            0% {{ stroke-dasharray: 0 1445; stroke-dashoffset: 0; }}
            50% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: 0; }}
            100% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: -1445; }}
        }}

        /* Complex Shape Trace (Draws and then fades/moves) */
        @keyframes draw-complex {{
            0% {{ stroke-dashoffset: 1200; }} /* Hidden */
            40% {{ stroke-dashoffset: 0; }}    /* Fully Drawn */
            60% {{ stroke-dashoffset: 0; opacity: 1; }} /* Pause */
            100% {{ stroke-dashoffset: -1200; opacity: 0; }} /* Disappear/Travel off */
        }}

        /* MORPH LOGIC: SHARPER SHURIKEN */
        /* Triangle: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%)
           Shuriken (3-Point Spike): polygon(50% 0%, 80% 80%, 50% 60%, 20% 80%)
           This creates a "Star Trek Badge" / Stealth Fighter shape.
        */

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
                    <path id="complexShape" d="M 200,10 L 330,60 L 390,190 L 330,320 L 200,390 L 70,320 L 10,190 L 70,60 Z" />
                </defs>
                <use href="#complexShape" class="trace-white" />
                <use href="#complexShape" class="trace-color" />
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