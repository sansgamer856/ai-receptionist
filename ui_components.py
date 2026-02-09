import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the N.A.O.M.I v7.0 UI (The Monolith).
    Minimalist. Industrial. Sharp radius changes.
    """
    
    # --- COLOR PALETTE ---
    colors = {
        "idle": "#00f3ff",      # Cyan
        "listening": "#d600ff", # Neon Purple
        "thinking": "#ffaa00",  # Amber/Gold
        "speaking": "#ffffff"   # White
    }
    
    c = colors.get(state, colors["idle"])
    
    # --- SVG PATH GENERATION ---
    # We are drawing a circle that "steps" between two radii:
    # r1 = 180px (Inner)
    # r2 = 230px (Outer)
    # The path draws arcs, then cuts straight radially to the next radius.
    
    # This path creates a shape with 3 "Outer Tabs" and 3 "Inner Recesses"
    # It looks like a heavy industrial lock ring.
    svg_path = """
    M 0 -180 
    A 180 180 0 0 1 155.8 -90     L 199 -115                    A 230 230 0 0 1 199 115       L 155.8 90                    A 180 180 0 0 1 -155.8 90     L -199 115                    A 230 230 0 0 1 -199 -115     L -155.8 -90                  A 180 180 0 0 1 0 -180        """
    
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

        .container {{
            position: relative;
            width: 600px;
            height: 600px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* --- 1. THE TEXT (GLISTENING) --- */
        .core-text {{
            position: absolute;
            z-index: 20;
            font-size: 42px; /* Massive, bold */
            font-weight: 900;
            letter-spacing: 10px;
            text-transform: uppercase;
            
            /* The Glisten Gradient */
            background: linear-gradient(
                110deg, 
                {c}40 0%, 
                {c}40 40%, 
                #ffffff 50%, 
                {c}40 60%, 
                {c}40 100%
            );
            background-size: 200% auto;
            
            /* Text Masking */
            color: transparent;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            /* Filters for "Solid" look behind the glisten */
            filter: drop-shadow(0 0 2px {c});
            
            animation: text-glisten 4s linear infinite;
        }}

        /* --- 2. THE INDUSTRIAL RING (SVG) --- */
        .svg-ring {{
            position: absolute;
            width: 600px;
            height: 600px;
            animation: spin 30s linear infinite;
            filter: drop-shadow(0 0 10px {c}60); /* Heavy Glow */
        }}

        path {{
            fill: none;
            stroke: {c};
            stroke-width: 15; /* THICK solid line */
            stroke-linecap: square; /* Sharp ends if we had them */
            stroke-linejoin: miter; /* Sharp corners on the cuts */
            
            transition: stroke 0.5s ease, filter 0.5s ease;
        }}

        /* --- ANIMATIONS --- */
        @keyframes text-glisten {{
            0% {{ background-position: 200% center; }}
            100% {{ background-position: -200% center; }}
        }}

        @keyframes spin {{
            100% {{ transform: rotate(360deg); }}
        }}

        @keyframes bounce {{ 
            0% {{ transform: scale(1); }} 
            100% {{ transform: scale(1.02); }} 
        }}

        /* --- STATE LOGIC --- */
        
        /* Thinking: Spin Fast, Brighten Ring */
        .thinking .svg-ring {{ animation-duration: 2s; }}
        .thinking path {{ stroke: #ffaa00; stroke-width: 18; filter: drop-shadow(0 0 20px #ffaa00); }}

        /* Listening: Slow spin, Pulse Text */
        .listening .svg-ring {{ animation-duration: 60s; }}
        .listening .core-text {{ filter: drop-shadow(0 0 15px {c}); letter-spacing: 12px; transition: letter-spacing 0.5s; }}

        /* Speaking: Audio Bounce */
        .speaking .container {{ animation: bounce 0.15s infinite alternate; }}
        .speaking path {{ stroke: #ffffff; filter: drop-shadow(0 0 15px #00f3ff); }}
        .speaking .core-text {{ background-image: linear-gradient(110deg, #fff 0%, #00f3ff 50%, #fff 100%); }}

    </style>
    </head>
    <body>
        <div class="container {state}">
            
            <svg class="svg-ring" viewBox="-250 -250 500 500">
                <path d="
                    M 0 -180 
                    A 180 180 0 0 1 127 -127
                    L 162 -162               
                    A 230 230 0 0 1 230 0    
                    L 180 0                  
                    A 180 180 0 0 1 127 127  
                    L 162 162                
                    A 230 230 0 0 1 0 230    
                    L 0 180                  
                    A 180 180 0 0 1 -127 127 
                    L -162 162               
                    A 230 230 0 0 1 -230 0   
                    L -180 0                 
                    A 180 180 0 0 1 -127 -127
                    L -162 -162              
                    A 230 230 0 0 1 0 -230   
                    L 0 -180                 
                    Z
                " />
            </svg>

            <div class="core-text">N.A.O.M.I.</div>
            
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)