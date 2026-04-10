"""Main entry point for the layered OS simulation."""

import streamlit as st

from config import APP_TITLE, FONT_FAMILY, PAGE_ICON
from animations.transitions import run_layer_transition
from utils.state import get_connected_device_names, get_system_state, init_system_state, reset_system
from utils.styling import get_animation_css, get_dark_theme_css, get_scanline_overlay
from views.device_view import render_device_view
from views.os_dashboard import render_dashboard
from views.room_view import render_room_view
from views.scheduler_view import render_scheduler_view


def init_styles() -> None:
    try:
        st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout="wide")
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
        st.markdown(get_scanline_overlay(), unsafe_allow_html=True)
        st.markdown(get_animation_css(), unsafe_allow_html=True)
        st.markdown(
            f"""
            <style>
            * {{ font-family: {FONT_FAMILY} !important; }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        return


def main() -> None:
    try:
        init_styles()
        init_system_state()
        state = get_system_state()
        layer = state.get("current_layer", "physical")

        with st.sidebar:
            st.markdown("### SYSTEM CONTROL")
            st.caption(f"Layer: {layer.upper()}")
            names = get_connected_device_names()
            st.caption("Devices: " + (", ".join(names) if names else "None"))
            if st.button("Reset System", use_container_width=True):
                run_layer_transition("Physical", logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"])
                reset_system()
                st.rerun()

        if layer == "physical":
            render_room_view()
        elif layer == "device":
            render_device_view()
        elif layer == "os":
            render_dashboard()
        elif layer == "scheduler":
            render_scheduler_view()
        else:
            state["current_layer"] = "physical"
            render_room_view()
    except Exception as exc:
        st.error(f"Kernel Panic: {exc}")


if __name__ == "__main__":
    main()
