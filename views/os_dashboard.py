"""OS reflection layer with teaching notes for viva."""

import streamlit as st

from animations.transitions import run_layer_transition
from utils.state import get_system_state, set_layer


def _derive_os_metrics(device_count: int, queue_size: int) -> dict:
    try:
        cpu_activity = min(100, 12 + device_count * 4 + queue_size * 6)
        io_pressure = min(100, queue_size * 10 + device_count * 3)
        bus_util = min(100, device_count * 7 + queue_size * 5)
        return {"cpu_activity": cpu_activity, "io_pressure": io_pressure, "bus_util": bus_util}
    except Exception:
        return {"cpu_activity": 0, "io_pressure": 0, "bus_util": 0}


def render_dashboard() -> None:
    try:
        state = get_system_state()
        devices = state["connected_devices"]
        queue = state["io_queue"]
        device_queues = state.get("device_queues", {})

        st.markdown("<div class='layer-shell'>", unsafe_allow_html=True)
        st.markdown("## > OS DASHBOARD LAYER")
        st.caption("Kernel reflection view driven by connected devices and queued I/O.")

        metric_data = _derive_os_metrics(len(devices), len(queue))
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CONNECTED DEVICES", len(devices))
        m2.metric("QUEUE SIZE", len(queue))
        m3.metric("CPU ACTIVITY", f"{metric_data['cpu_activity']}%")
        m4.metric("I/O PRESSURE", f"{metric_data['io_pressure']}%")
        st.write(f"Current Head Position: {state['current_head']}")
        st.write(f"Active Algorithm: {state['active_algorithm']}")
        active_devices_text = ", ".join([d.get("name", "Unknown") for d in devices]) if devices else "None"
        st.write(f"Active Devices: {active_devices_text}")

        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("### > CONNECTED DEVICE MAP")
            if devices:
                st.dataframe(
                    [{"Device": d.get("name", "Unknown"), "Status": d.get("status", "INITIALIZING")} for d in devices],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No connected devices. Return to previous layers to attach hardware.")
            st.markdown("### > DEVICE QUEUE SNAPSHOT")
            if device_queues:
                queue_rows = [{"Device": name, "Pending Requests": len(items), "Queue": str(items)} for name, items in device_queues.items()]
                st.dataframe(queue_rows, use_container_width=True, hide_index=True)
            else:
                st.info("No device-specific queues yet.")

        with right:
            st.markdown("### > TEACHING NOTES")
            st.markdown("<div class='layer-subpanel'>", unsafe_allow_html=True)
            st.write("I/O Queue:")
            st.caption("A list of pending input/output requests waiting to be serviced by the OS.")
            st.write("Service Time Formula:")
            st.code("|current_head - next_track|", language="text")
            st.caption("Analogy: Like moving an elevator between floors to pick passengers.")
            st.write("Why this layer matters:")
            st.caption("It links hardware status to scheduler readiness and system load.")
            st.markdown("</div>", unsafe_allow_html=True)

        n1, n2 = st.columns(2)
        if n1.button("> BACK TO DEVICE LAYER", use_container_width=True):
            run_layer_transition(
                "Device",
                logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"],
            )
            set_layer("device")
            st.rerun()
        if n2.button("> ENTER SCHEDULER EXECUTION", type="primary", use_container_width=True):
            run_layer_transition("Scheduler")
            set_layer("scheduler")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"OS layer fault: {exc}")
