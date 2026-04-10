"""Cinematic transition sequences for layer entry."""

import time
from typing import Iterable

import streamlit as st

from .lottie_loader import render_lottie_animation

TRANSITION_STEPS = [
    "[INPUT RECEIVED]",
    "[LOCATING DEVICE]",
    "[SIGNAL UNSTABLE]",
    "[ACCESSING SYSTEM]",
]


def run_layer_transition(next_layer_label: str, logs: Iterable[str] | None = None) -> None:
    """Shows a staged glitch-style sequence before entering next layer."""
    try:
        step_logs = list(logs) if logs else TRANSITION_STEPS
        title_slot = st.empty()
        loader_slot = st.empty()
        log_slot = st.empty()

        title_slot.markdown(f"### > ENTERING {next_layer_label.upper()} LAYER")
        render_lottie_animation("assets/animations/processing.json", height=120, key=f"lottie-{next_layer_label}")

        lines = []
        for step in step_logs:
            lines.append(step)
            log_slot.code("\n".join(lines), language="text")
            time.sleep(0.18)

        # Glitch correction moment
        log_slot.markdown("<p class='glitch'>[ACCESS DNIED]</p>", unsafe_allow_html=True)
        time.sleep(0.14)
        log_slot.code("\n".join(lines + ["[ACCESS GRANTED]"]), language="text")
        time.sleep(0.2)

        # Brief blackout frame
        black_frame = st.empty()
        black_frame.markdown("<div style='height:120px;background:#000;'></div>", unsafe_allow_html=True)
        time.sleep(0.16)
        black_frame.empty()

        loader_slot.empty()
        title_slot.empty()
        log_slot.empty()
    except Exception:
        return
