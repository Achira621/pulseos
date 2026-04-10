"""Styling helpers for the analog terminal theme."""
from config import COLORS, FONT_FAMILY

def get_dark_theme_css() -> str:
    """Returns the base dark theme CSS based on config tokens."""
    try:
        return f"""
        <style>
        :root {{
            --bg: {COLORS["background"]};
            --panel: {COLORS["panel"]};
            --text: {COLORS["text"]};
            --accent: {COLORS["accent"]};
            --warning: {COLORS["warning"]};
            --error: {COLORS["error"]};
            --font-mono: {FONT_FAMILY};
        }}
        
        .stApp {{
            background-color: var(--bg);
            color: var(--text);
            overflow: hidden;
        }}

        [data-testid="stHeader"], footer {{
            display: none !important;
        }}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            overflow: hidden !important;
        }}

        .layer-shell {{
            min-height: 86vh;
            max-height: 86vh;
            overflow: hidden;
            border: 1px solid rgba(107, 143, 113, 0.4);
            background: linear-gradient(180deg, rgba(26,26,26,0.95), rgba(10,10,10,0.95));
            padding: 0.75rem 1rem;
        }}

        .layer-subpanel {{
            background: rgba(22,22,22,0.9);
            border: 1px solid rgba(107, 143, 113, 0.3);
            padding: 0.5rem 0.7rem;
        }}
        
        /* Terminal styling */
        .stMarkdown div, .stMarkdown p {{
            color: var(--text) !important;
        }}
        
        /* Custom component styling */
        .stButton > button {{
            background: var(--panel) !important;
            border: 1px solid var(--accent) !important;
            color: var(--text) !important;
            border-radius: 2px !important;
            text-transform: uppercase;
        }}
        
        .stButton > button:hover {{
            border-color: var(--warning) !important;
            color: var(--warning) !important;
        }}
        
        .section-header {{
            color: var(--accent);
            letter-spacing: 2px;
            font-weight: bold;
            border-bottom: 1px solid var(--accent);
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}

        .device-card {{
            border: 1px dashed rgba(107, 143, 113, 0.35);
            padding: 0.45rem;
            margin-bottom: 0.35rem;
            font-size: 0.85rem;
        }}

        .device-plugged {{
            border-left: 3px solid #6b8f71;
        }}

        .device-unplugged {{
            border-left: 3px solid #5f5f5f;
            opacity: 0.75;
        }}
        
        </style>
        """
    except Exception:
        return "<style>body{background:#0d0d0d;}</style>"

def get_scanline_overlay() -> str:
    """Returns the CRT scanline and noise overlay CSS."""
    try:
        return """
        <style>
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15),
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 100;
        }
        
        .stApp::after {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(18, 16, 16, 0.1);
            opacity: 0.1;
            pointer-events: none;
            z-index: 99;
            filter: contrast(150%) brightness(100%);
        }
        </style>
        """
    except Exception:
        return ""


def get_animation_css() -> str:
    """Returns lightweight flicker helpers used by the analog UI."""
    try:
        return """
        <style>
        @keyframes crt-flicker {
            0%, 100% { opacity: 0.98; }
            50% { opacity: 0.9; }
        }

        .crt-flicker {
            animation: crt-flicker 0.18s step-end 4;
        }

        .terminal-log {
            padding: 0.45rem 0.6rem;
            margin-bottom: 0.3rem;
            background: rgba(12, 12, 12, 0.88);
            border-left: 2px solid var(--accent);
            color: var(--text);
        }

        .glitch {
            text-shadow: 1px 0 #b25e5e, -1px 0 #6b8f71;
            animation: crt-flicker 0.14s step-end 6;
        }
        </style>
        """
    except Exception:
        return ""
