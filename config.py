"""Central configuration for tokens, colors, and settings.

This module keeps compatibility aliases because the current project still
contains a mix of earlier and refactored imports.
"""

APP_TITLE = "OS I/O SCHEDULER :: ANALOG 1.0"
PAGE_ICON = "CRT"

COLORS = {
    "background": "#0d0d0d",
    "bg": "#0d0d0d",
    "panel": "#1a1a1a",
    "panel_alt": "#151515",
    "text": "#d6d6d6",
    "accent": "#6b8f71",
    "warning": "#a5855d",
    "warn": "#a5855d",
    "error": "#b25e5e",
    "danger": "#b25e5e",
    "muted": "#8c968f",
    "grid": "#263028",
}

FONT_FAMILY = "'Courier New', Courier, monospace"
FONTS = FONT_FAMILY

EFFECTS = {
    "scanline_opacity": 0.04,
    "flicker_active": True,
    "grain_opacity": 0.05,
}

DEFAULT_HEAD = 500
MAX_TRACKS = 1000
TOTAL_TRACKS = MAX_TRACKS
