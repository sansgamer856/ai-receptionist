import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v7.0 UI (Erratic Tech Ring).
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

        /* --- THE TITLE (PRESERVED PERFECT GLISTEN) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 8px;
            
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

        /* --- 1. MEDIUM SOLID RADIAL LINE --- */
        .ring-solid {{
            position: absolute;
            width: 220px; height: 220px;
            border-radius: 50%;
            border: 4px solid {c}; /* Medium thickness */
            opacity: 1; /* Solid 100% */
            box-shadow: 0 0 10px {c}40;
            
            /* Erratic Movement 1 */
            animation: erratic-spin-1 12s cubic-bezier(0.68, -0.6, 0.32, 1.6) infinite;
        }}

        /* --- 2. TECH EXTRUSIONS (UNIQUE ELEMENTS) --- */
        .ring-tech {{
            position: absolute;
            width: 250px; height: 250px; /* Hugs the medium line closely */
            border-radius: 50%;
            
            /* Creating the "Extruding Elements" using Conic Gradients */
            /* This makes solid blocks (100% opacity) of varying sizes */
            background: conic-gradient(
                transparent 0deg 10deg,
                {c} 10deg 15deg,   /* Block 1 */
                transparent 15deg 40deg,
                {c} 40deg 50deg,   /* Block 2 (Larger) */
                transparent 50deg 90deg,
                {c} 90deg 92deg,   /* Block 3 (Tiny) */
                transparent 92deg 140deg,
                {c} 140deg 160deg, /* Block 4 (Huge) */
                transparent 160deg 200deg,
                {c} 200deg 205deg, /* Block 5 */
                transparent 205deg 260deg,
                {c} 260deg 275deg, /* Block 6 */
                transparent 275deg 360deg
            );
            
            /* Mask center to turn the pie chart into a ring with blocks */
            -webkit-mask: radial-gradient(farthest-side, transparent 75%, black 76%);
            mask: radial-gradient(farthest-side, transparent 75%, black 76%);
            
            /* Erratic Movement 2 (Different timing) */
            animation: erratic-spin-2 9s cubic-bezier(0.4, 0.0, 0.2, 1) infinite;
        }}

        /* --- 3. THINNER OUTER LINE --- */
        .ring-thin {{
            position: absolute;
            width: 280px; height: 280px; /* Slightly outside the tech ring */
            border-radius: 50%;
            border: 1px solid {c}; /* Thin */
            opacity: 0.8;
            
            /* Erratic Movement 3 */
            animation: erratic-spin-1 15s cubic-bezier(0.68, -0.6, 0.32, 1.6) infinite reverse;
        }}

        /* --- ERRATIC ANIMATIONS (Random-ish behavior) --- */
        
        /* Profile 1: Overshoots and reverses */
        @keyframes erratic-spin-1 {{
            0% {{ transform: rotate(0deg); }}
            20% {{ transform: rotate(120deg); }} /* Fast Fwd */
            40% {{ transform: rotate(90deg); }}  /* Short Reverse */
            60% {{ transform: rotate(240deg); }} /* Fast Fwd */
            80% {{ transform: rotate(220deg); }} /* Short Reverse */
            100% {{ transform: rotate(360deg); }}
        }}

        /* Profile 2: Pauses and jerks */
        @keyframes erratic-spin-2 {{
            0% {{ transform: rotate(0deg); }}
            30% {{ transform: rotate(-50deg); }} /* Reverse */
            50% {{ transform: rotate(20deg); }}  /* Fwd */
            70% {{ transform: rotate(10deg); }}  /* Pause/Slow Reverse */
            100% {{ transform: rotate(360deg); }}
        }}

        @keyframes text-shimmer {{ 
            0% {{ background-position: 200% center; }} 
            100% {{ background-position: -200% center; }} 
        }}
        
        @keyframes bounce {{ 
            0% {{ transform: scale(1); }} 
            100% {{ transform: scale(1.02); }} 
        }}

        /* --- STATE LOGIC --- */
        
        /* THINKING: Speed up drastically */
        .thinking .ring-solid {{ animation-duration: 2s; }}
        .thinking .ring-tech {{ animation-duration: 1.5s; }}
        .thinking .ring-thin {{ animation-duration: 3s; }}
        
        /* SPEAKING: Bounce */
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        
        /* LISTENING: Expand slightly */
        .listening .ring-thin {{ transform: scale(1.1); transition: transform 1s; }}

    </style>
    </head>
    <body>
        <div class="reactor {state}">
            <div class="ring-thin"></div>

            <div class="ring-tech"></div>

            <div class="ring-solid"></div>

            <div class="core-text">N.A.O.M.I.</div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)