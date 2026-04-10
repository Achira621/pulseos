"""Device connection layer: handshake and driver activation."""

import streamlit as st

from animations.transitions import run_layer_transition
from utils.state import get_system_state, initialize_connected_devices, set_layer


def render_device_view() -> None:
    try:
        state = get_system_state()
        st.markdown("<div class='layer-shell'>", unsafe_allow_html=True)
        st.markdown("## > DEVICE CONNECTION LAYER")
        st.caption("Detected hardware is mapped to drivers and interrupt channels.")

        devices = state["connected_devices"]
        if not devices:
            st.warning("No connected devices found.")
            if st.button("> RETURN TO PHYSICAL ROOM", use_container_width=True):
                run_layer_transition(
                    "Physical",
                    logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"],
                )
                set_layer("physical")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            return

        left, right = st.columns([1.3, 1])
        with left:
            st.markdown("### > HARDWARE STATUS TABLE")
            rows = [
                {
                    "Device": device.get("name", "Unknown"),
                    "Status": device.get("status", "INITIALIZING"),
                    "Driver": "Loaded" if device.get("status") == "READY" else "Pending",
                }
                for device in devices
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)

            if st.button("> RUN HANDSHAKE SEQUENCE", type="primary", use_container_width=True):
                initialize_connected_devices()
                st.success("Handshake complete: all connected devices are READY.")
                st.rerun()

        with right:
            st.markdown("### > KERNEL LOG FEED")
            log_feed = state.get("device_event_log", [])
            if not log_feed:
                st.info("[DEVICE DETECTED] logs will appear after hardware events.")
            else:
                for line in log_feed[-18:]:
                    st.markdown(f"<div class='terminal-log'>{line}</div>", unsafe_allow_html=True)

            if st.button("> ENTER OS DASHBOARD", use_container_width=True):
                run_layer_transition("OS")
                set_layer("os")
                st.rerun()
            if st.button("> BACK TO PHYSICAL ROOM", use_container_width=True):
                run_layer_transition(
                    "Physical",
                    logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"],
                )
                set_layer("physical")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Device layer fault: {exc}")
