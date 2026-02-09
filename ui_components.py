import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v9.0 UI (Morphing Geometry).
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

        /* --- TITLE (SMALLER) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 20px; /* Smaller */
            font-weight: 900;
            letter-spacing: 6px;
            background: linear-gradient(90deg, {c}40 0%, {c} 50%, {c}40 100%);
            background-size: 200% auto;
            color: #000;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 3s linear infinite;
        }}

        /* --- 0. BACKGROUND TRACER (SVG) --- */
        /* Creates and removes the circle continuously */
        .svg-tracer {{
            position: absolute;
            width: 480px; height: 480px;
            z-index: 0;
            animation: spin-slow 30s linear infinite;
        }}
        
        .tracer-path {{
            fill: none;
            stroke: {c};
            stroke-width: 2;
            stroke-linecap: round;
            /* Dasharray: Gap is circumference (~1445 for r=230) */
            stroke-dasharray: 1445; 
            stroke-dashoffset: 1445; /* Start hidden */
            opacity: 0.5;
            animation: trace-circle 6s ease-in-out infinite;
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

        /* --- 3. MORPHING TRIANGLES -> STARS --- */
        .ring-cardinal {{
            position: absolute;
            width: 100%; height: 100%;
            pointer-events: none;
        }}

        /* The container for each morphing element */
        .cardinal-point {{
            position: absolute;
            left: 50%; top: 50%;
            width: 40px; height: 40px;
            background: {c};
            
            /* Initial shape: Triangle (Arrowhead) */
            /* Using 4 points to match the Star's 4 points for smooth morphing */
            clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%);
            
            /* Center the pivot */
            transform-origin: center center;
            box-shadow: 0 0 15px {c};
        }}

        /* Animations for each direction */
        /* They Move OUT and Morph shape, then Move IN and Revert */
        
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

        /* TRACER: Draws (0 to Full) then Erases (Full to 0 offset/gap) */
        @keyframes trace-circle {{
            0% {{ stroke-dasharray: 0 1445; stroke-dashoffset: 0; }} /* Empty */
            50% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: 0; }} /* Full Circle Drawn */
            100% {{ stroke-dasharray: 1445 1445; stroke-dashoffset: -1445; }} /* Circle "Erased" by offset */
        }}

        /* MORPH LOGIC: 
           Translate moves it OUT.
           Clip-path changes from Triangle (Arrow) to Star (Diamond Spike).
        */
        @keyframes morph-north {{
            0%, 100% {{ transform: translate(-50%, -200px) rotate(0deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }} /* In (Triangle) */
            50% {{ transform: translate(-50%, -260px) rotate(0deg); clip-path: polygon(50% 0%, 80% 50%, 50% 100%, 20% 50%); }} /* Out (Star) */
        }}
        @keyframes morph-south {{
            0%, 100% {{ transform: translate(-50%, 160px) rotate(180deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(-50%, 220px) rotate(180deg); clip-path: polygon(50% 0%, 80% 50%, 50% 100%, 20% 50%); }}
        }}
        @keyframes morph-east {{
            0%, 100% {{ transform: translate(160px, -50%) rotate(90deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(220px, -50%) rotate(90deg); clip-path: polygon(50% 0%, 80% 50%, 50% 100%, 20% 50%); }}
        }}
        @keyframes morph-west {{
            0%, 100% {{ transform: translate(-200px, -50%) rotate(-90deg); clip-path: polygon(50% 0%, 100% 100%, 50% 80%, 0% 100%); }}
            50% {{ transform: translate(-260px, -50%) rotate(-90deg); clip-path: polygon(50% 0%, 80% 50%, 50% 100%, 20% 50%); }}
        }}

        /* --- STATE LOGIC --- */
        .thinking .ring-arc {{ border-color: {c}; animation-duration: 2s; }}
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            
            <svg class="svg-tracer" viewBox="0 0 500 500">
                <circle class="tracer-path" cx="250" cy="250" r="230" />
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