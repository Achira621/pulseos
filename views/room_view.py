"""Physical room layer with plug/unplug style interaction."""

import streamlit as st

from animations.transitions import run_layer_transition
from utils.state import DEVICE_CATALOG, connect_device, get_system_state, is_device_connected, set_layer


def render_room_view() -> None:
    try:
        state = get_system_state()
        st.markdown("<div class='layer-shell'>", unsafe_allow_html=True)
        st.markdown("## > PHYSICAL ROOM")
        st.caption("Plug hardware modules into the machine backplane.")

        c1, c2 = st.columns([2, 1.2])
        with c1:
            try:
                st.image("assets/ui/room.png", use_container_width=True)
            except Exception:
                st.info("Room feed unavailable. Switch to textual hardware console.")
            st.markdown("<div class='layer-subpanel'>", unsafe_allow_html=True)
            st.markdown("### > DEVICE RACK STATE")
            for name in DEVICE_CATALOG:
                connected = is_device_connected(name)
                badge = "PLUGGED" if connected else "UNPLUGGED"
                css_class = "device-plugged" if connected else "device-unplugged"
                cable = "[=====CABLE CONNECTED=====]" if connected else "[-----NO CABLE-----]"
                st.markdown(
                    f"<div class='device-card {css_class}'><b>{name}</b> | {badge}<br><small>{cable}</small></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("### > PLUG ACTIONS")
            selected_device = st.selectbox("Select Device to Plug", DEVICE_CATALOG, index=0)
            if st.button("PLUG SELECTED DEVICE", use_container_width=True):
                if connect_device(selected_device):
                    st.success(f"{selected_device} plugged in.")
                else:
                    st.warning(f"{selected_device} already connected.")

            st.divider()
            st.write(f"Connected Devices: {len(state['connected_devices'])}")
            if st.button("> ENTER DEVICE CONNECTION LAYER", type="primary", use_container_width=True):
                if not state["connected_devices"]:
                    st.error("No connected hardware. Plug at least one device first.")
                else:
                    run_layer_transition("Device")
                    set_layer("device")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Physical layer fault: {exc}")
