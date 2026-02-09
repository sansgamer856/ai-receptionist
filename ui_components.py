import streamlit as st
import streamlit.components.v1 as components

def render_jarvis_ui(state="idle"):
    """
    Renders the ADVANCED N.A.O.M.I DASHBOARD.
    """
    
    # --- COLOR PALETTE (Cyberpunk HUD) ---
    colors = {
        "idle": {"core": "#00f3ff", "glow": "rgba(0, 243, 255, 0.5)", "alert": "#00f3ff"},
        "listening": {"core": "#bf00ff", "glow": "rgba(191, 0, 255, 0.6)", "alert": "#ff0080"},
        "thinking": {"core": "#ffcc00", "glow": "rgba(255, 204, 0, 0.6)", "alert": "#ffaa00"},
        "speaking": {"core": "#ffffff", "glow": "rgba(255, 255, 255, 0.8)", "alert": "#00f3ff"}
    }
    
    c = colors.get(state, colors["idle"])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

        body {{
            background-color: transparent;
            color: {c['core']};
            font-family: 'Orbitron', sans-serif;
            margin: 0;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 600px;
        }}

        /* --- GRID LAYOUT --- */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            grid-template-rows: 1fr 3fr 1fr;
            width: 100%;
            height: 100%;
            max-width: 900px;
            gap: 10px;
            padding: 20px;
            box-sizing: border-box;
        }}

        .panel {{
            border: 1px solid rgba(0, 243, 255, 0.1);
            background: rgba(0, 10, 20, 0.4);
            position: relative;
            padding: 10px;
            display: flex;
            flex-direction: column;
        }}

        .panel::before {{ /* Corner Accents */
            content: ''; position: absolute; top: 0; left: 0; width: 10px; height: 10px;
            border-top: 2px solid {c['core']}; border-left: 2px solid {c['core']};
        }}
        .panel::after {{
            content: ''; position: absolute; bottom: 0; right: 0; width: 10px; height: 10px;
            border-bottom: 2px solid {c['core']}; border-right: 2px solid {c['core']};
        }}

        /* --- MODULES --- */
        .top-left {{ grid-column: 1; grid-row: 1; }}
        .top-right {{ grid-column: 3; grid-row: 1; text-align: right; }}
        .center-stage {{ grid-column: 2; grid-row: 1 / span 3; display: flex; justify-content: center; align-items: center; }}
        .bottom-left {{ grid-column: 1; grid-row: 3; }}
        .bottom-right {{ grid-column: 3; grid-row: 3; text-align: right; }}
        .side-stats {{ grid-column: 1; grid-row: 2; display: flex; flex-direction: column; gap: 15px; justify-content: center; }}
        .side-logs {{ grid-column: 3; grid-row: 2; font-size: 10px; opacity: 0.7; overflow: hidden; }}

        /* --- TEXT STYLES --- */
        h3 {{ margin: 0 0 5px 0; font-size: 12px; letter-spacing: 2px; opacity: 0.8; }}
        .val {{ font-size: 18px; font-weight: bold; text-shadow: 0 0 10px {c['glow']}; }}
        .log-line {{ border-bottom: 1px solid rgba(0,255,255,0.1); padding: 2px 0; }}

        /* --- BARS --- */
        .bar-container {{ width: 100%; height: 6px; background: rgba(255,255,255,0.1); margin-top: 5px; }}
        .bar-fill {{ height: 100%; background: {c['core']}; width: 0%; animation: load-bar 3s infinite ease-in-out; }}
        .bar-fill.random1 {{ width: 45%; animation-duration: 2s; }}
        .bar-fill.random2 {{ width: 70%; animation-duration: 4s; }}

        /* --- THE REACTOR (CENTER) --- */
        .reactor {{
            position: relative;
            width: 300px;
            height: 300px;
        }}
        
        .ring {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            border: 1px solid transparent;
        }}

        .outer-ring {{
            width: 280px; height: 280px;
            border: 2px dashed {c['core']};
            animation: spin 20s linear infinite;
            opacity: 0.3;
        }}

        .mid-ring {{
            width: 220px; height: 220px;
            border-top: 4px solid {c['core']};
            border-bottom: 4px solid {c['core']};
            box-shadow: 0 0 15px {c['glow']};
            animation: spin-reverse 8s linear infinite;
        }}

        .inner-ring {{
            width: 140px; height: 140px;
            border-left: 8px solid {c['alert']};
            border-right: 2px solid {c['alert']};
            animation: spin 3s cubic-bezier(0.4, 0.0, 0.2, 1) infinite;
        }}

        .core-dot {{
            width: 40px; height: 40px;
            background: {c['core']};
            border-radius: 50%;
            box-shadow: 0 0 40px {c['core']};
            animation: pulse 1s infinite alternate;
        }}

        /* --- STATE ANIMATIONS --- */
        .listening .mid-ring {{ animation-duration: 30s; border-color: {c['core']}; }}
        .listening .inner-ring {{ animation: breathe 2s infinite ease-in-out; border-style: dotted; }}
        
        .thinking .mid-ring {{ animation: spin 0.5s linear infinite; border-width: 2px; }}
        .thinking .inner-ring {{ animation: spin-reverse 1s linear infinite; border-width: 4px; }}
        
        .speaking .reactor {{ animation: bounce 0.2s infinite alternate; }}
        
        @keyframes spin {{ 100% {{ transform: translate(-50%, -50%) rotate(360deg); }} }}
        @keyframes spin-reverse {{ 100% {{ transform: translate(-50%, -50%) rotate(-360deg); }} }}
        @keyframes pulse {{ 0% {{ opacity: 0.5; transform: translate(-50%, -50%) scale(0.8); }} 100% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.2); }} }}
        @keyframes breathe {{ 0% {{ transform: translate(-50%, -50%) scale(1); }} 50% {{ transform: translate(-50%, -50%) scale(1.1); }} 100% {{ transform: translate(-50%, -50%) scale(1); }} }}
        @keyframes load-bar {{ 0% {{ width: 10%; }} 50% {{ width: 80%; }} 100% {{ width: 10%; }} }}
        @keyframes bounce {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.02); }} }}

    </style>
    </head>
    <body>
        <div class="dashboard-grid {state}">
            
            <div class="panel top-left">
                <h3>SYS.STATUS</h3>
                <div class="val">ONLINE</div>
                <div class="bar-container"><div class="bar-fill"></div></div>
            </div>

            <div class="side-stats">
                <div>
                    <h3>CPU LOAD</h3>
                    <div class="bar-container"><div class="bar-fill random1"></div></div>
                </div>
                <div>
                    <h3>MEMORY</h3>
                    <div class="bar-container"><div class="bar-fill random2"></div></div>
                </div>
                <div>
                    <h3>UPLINK</h3>
                    <div class="val" style="font-size: 12px">450 Mb/s</div>
                </div>
            </div>

            <div class="center-stage">
                <div class="reactor">
                    <div class="ring outer-ring"></div>
                    <div class="ring mid-ring"></div>
                    <div class="ring inner-ring"></div>
                    <div class="ring core-dot"></div>
                </div>
            </div>

            <div class="panel top-right">
                <h3>MODE</h3>
                <div class="val">{state.upper()}</div>
            </div>

            <div class="panel side-logs">
                <div class="log-line">> INITIALIZING PROTOCOL...</div>
                <div class="log-line">> CONNECTING TO G.CAL...</div>
                <div class="log-line">> SECURE LINK ESTABLISHED</div>
                <div class="log-line">> WAITING FOR INPUT...</div>
            </div>

            <div class="panel bottom-left">
                <h3>COORDINATES</h3>
                <div style="font-size: 10px">40.7128° N, 74.0060° W</div>
            </div>

            <div class="panel bottom-right">
                <h3>N.A.O.M.I. v2.4</h3>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    # We increase height to accommodate the dashboard
    components.html(html_code, height=600)