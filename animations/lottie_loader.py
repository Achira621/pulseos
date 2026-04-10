"""Lottie animation helpers with fault-tolerant fallback."""

import json
from pathlib import Path
from typing import Optional

import streamlit as st

try:
    from streamlit_lottie import st_lottie
except Exception:  # pragma: no cover
    st_lottie = None


def load_lottie_file(path: str) -> Optional[dict]:
    try:
        file_path = Path(path)
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def render_lottie_animation(path: str, height: int = 150, key: str = "layer-loader") -> None:
    try:
        payload = load_lottie_file(path)
        if payload and st_lottie:
            st_lottie(payload, height=height, key=key, speed=1.0, loop=True)
        else:
            st.caption("[ANIMATION MODULE OFFLINE]")
    except Exception:
        st.caption("[ANIMATION MODULE OFFLINE]")
