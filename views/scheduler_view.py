"""Scheduler execution layer with teaching overlays and comparison."""

import streamlit as st

from core.metrics import calculate_result_metrics
from core.scheduler import compare_algorithms, run_algorithm
from utils.state import (
    add_device_request,
    add_io_request,
    clear_io_queue,
    get_connected_device_names,
    get_system_state,
    pop_last_device_request,
    remove_io_request,
    set_layer,
)
from animations.transitions import run_layer_transition

ALGO_NOTES = {
    "FCFS": {
        "what": "Serves requests in arrival order.",
        "why": "Simple and fair for basic scheduling demonstration.",
        "logic": "Process queue from first to last.",
        "pros": "Easy to implement, no starvation in simple queues.",
        "cons": "Can produce high seek movement.",
    },
    "SSTF": {
        "what": "Picks the request closest to current head position.",
        "why": "Usually reduces total seek time.",
        "logic": "Choose minimum |current_head - request_track| repeatedly.",
        "pros": "Fast average seek behavior.",
        "cons": "Far requests may wait too long (starvation risk).",
    },
    "SCAN": {
        "what": "Moves head in one direction servicing tracks, then reverses.",
        "why": "Balances fairness and performance.",
        "logic": "Sort requests by track and traverse like an elevator.",
        "pros": "Predictable and fairer than SSTF.",
        "cons": "Can still travel long distances at queue edges.",
    },
}


def _auto_select_algorithm(queue_size: int) -> str:
    try:
        if queue_size <= 3:
            return "FCFS"
        if queue_size <= 8:
            return "SSTF"
        return "SCAN"
    except Exception:
        return "FCFS"


def _priority_sorted(queue):
    try:
        return sorted(queue, key=lambda req: req.priority)
    except Exception:
        return queue


def _render_stepwise_explainer(result) -> None:
    try:
        st.markdown("#### Movement Step-by-Step")
        if not result or not result.execution_order:
            st.caption("Run an algorithm to view step-by-step head movement.")
            return
        rows = []
        for idx, req_id in enumerate(result.execution_order):
            rows.append(
                {
                    "Step": idx + 1,
                    "Request ID": req_id,
                    "Head Position": result.head_positions[idx],
                    "Seek Time": round(result.seek_times[idx], 2),
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
    except Exception:
        st.caption("Stepwise movement view unavailable.")


def render_scheduler_view() -> None:
    try:
        state = get_system_state()
        devices = state["connected_devices"]
        queue = state["io_queue"]
        device_names = get_connected_device_names()

        st.markdown("<div class='layer-shell'>", unsafe_allow_html=True)
        st.markdown("## > SCHEDULER EXECUTION LAYER")
        st.caption("Run FCFS / SSTF / SCAN with teaching overlays and comparison.")

        if not devices:
            st.error("No I/O devices available")
            if st.button("> RETURN TO PHYSICAL ROOM", use_container_width=True):
                run_layer_transition(
                    "Physical",
                    logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"],
                )
                set_layer("physical")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.write("Active Devices: " + ", ".join(device_names))
        st.caption("Scheduler is processing requests for connected I/O devices.")

        # Input + queue control
        st.markdown("### > I/O REQUEST INPUT")
        c0, c1, c2, c3 = st.columns(4)
        target_device = c0.selectbox("Target Device", options=device_names, index=0)
        track = c1.number_input("Track Number", min_value=0, max_value=999, value=500)
        priority = c2.slider("Priority", min_value=1, max_value=10, value=5)
        burst = c3.number_input("Burst Time", min_value=1.0, max_value=100.0, value=10.0)

        a1, a2, a3 = st.columns(3)
        if a1.button("ADD I/O REQUEST", use_container_width=True):
            if target_device in {"Disk Drive", "Disk"}:
                if add_io_request(int(track), int(priority), float(burst)):
                    st.success(f"Disk request added at track {int(track)}.")
                    st.rerun()
                else:
                    st.error("Failed to add request.")
            else:
                payload = f"Job{state['request_counter'] + 1}-P{priority}"
                if add_device_request(target_device, payload):
                    st.success(f"{target_device} request added ({payload}).")
                    st.rerun()
                else:
                    st.error("Failed to add request.")
        if a2.button("REMOVE LAST REQUEST", use_container_width=True):
            if target_device in {"Disk Drive", "Disk"}:
                if queue and remove_io_request(queue[-1].request_id):
                    st.success("Last disk request removed.")
                    st.rerun()
                else:
                    st.info("No removable disk request found.")
            else:
                if pop_last_device_request(target_device):
                    st.success(f"Last request removed from {target_device}.")
                    st.rerun()
                else:
                    st.info(f"No removable request found for {target_device}.")
        if a3.button("CLEAR QUEUE", use_container_width=True):
            clear_io_queue()
            st.rerun()

        st.markdown("### > DEVICE-AWARE QUEUES")
        device_queues = state.get("device_queues", {})
        for name in device_names:
            st.markdown(f"**{name}** -> {device_queues.get(name, [])}")
        if queue:
            st.markdown("#### Disk Queue Details")
            st.dataframe(
                [{"ID": req.request_id, "Track": req.track, "Priority": req.priority, "Burst": req.burst_time} for req in queue],
                use_container_width=True,
                hide_index=True,
            )

        # Algorithm control + teaching overlay
        st.markdown("### > ALGORITHM CONTROL")
        b1, b2, b3 = st.columns(3)
        if b1.button("FCFS", use_container_width=True):
            state["active_algorithm"] = "FCFS"
        if b2.button("SSTF", use_container_width=True):
            state["active_algorithm"] = "SSTF"
        if b3.button("SCAN", use_container_width=True):
            state["active_algorithm"] = "SCAN"

        if st.button("Auto Optimize", type="primary", use_container_width=True):
            chosen = _auto_select_algorithm(len(queue))
            state["active_algorithm"] = chosen
            if chosen == "SSTF":
                st.success("System selected SSTF because it minimizes seek time by choosing closest request.")
            elif chosen == "SCAN":
                st.success("System selected SCAN for large queues to balance movement and fairness.")
            else:
                st.success("System selected FCFS for small queue simplicity.")

        current_algo = state["active_algorithm"]
        notes = ALGO_NOTES.get(current_algo, ALGO_NOTES["FCFS"])
        st.markdown("### > TEACHING OVERLAY")
        st.markdown("<div class='layer-subpanel'>", unsafe_allow_html=True)
        st.write(f"Algorithm: {current_algo}")
        st.caption(f"What it does: {notes['what']}")
        st.caption(f"Why used: {notes['why']}")
        st.code(notes["logic"], language="text")
        st.caption(f"Pros: {notes['pros']}")
        st.caption(f"Cons: {notes['cons']}")
        st.markdown("</div>", unsafe_allow_html=True)

        use_priority = st.checkbox("Apply priority sorting before algorithm", value=False)
        execution_queue = _priority_sorted(queue) if use_priority else list(queue)

        run_col, compare_col = st.columns(2)
        if run_col.button("RUN SELECTED ALGORITHM", use_container_width=True):
            disk_ready = any(name in {"Disk Drive", "Disk"} for name in device_names)
            if not disk_ready:
                st.warning("No Disk device connected. Serving non-disk queues in FCFS order only.")
                for name in device_names:
                    if name in {"Disk Drive", "Disk"}:
                        continue
                    items = state.get("device_queues", {}).get(name, [])
                    if items:
                        state["device_event_log"].append(f"[SERVICE] {name} -> {items[0]}")
                st.success("Non-disk device queues serviced.")
            elif not queue:
                st.error("Disk queue empty. Cannot execute disk scheduling.")
            else:
                result = run_algorithm(current_algo, execution_queue, state["current_head"])
                state["last_result"] = result
                if result.head_positions:
                    state["current_head"] = result.head_positions[-1]
                state["device_event_log"].append(f"[SERVICE] Disk -> {result.execution_order}")
                st.success("Execution complete.")

        if compare_col.button("COMPARE FCFS / SSTF / SCAN", use_container_width=True):
            if not queue:
                st.warning("Queue empty. Add requests for comparison.")
            else:
                results = compare_algorithms(execution_queue, state["current_head"])
                rows = []
                for algo_name, result in results.items():
                    stats = calculate_result_metrics(result)
                    rows.append(
                        {
                            "Algorithm": algo_name,
                            "Order": str(result.execution_order),
                            "Total Time": round(stats["total_seek"], 2),
                            "Avg Time": round(stats["average_seek"], 2),
                        }
                    )
                st.markdown("#### Performance Comparison")
                st.dataframe(rows, use_container_width=True, hide_index=True)
                st.caption("Lower total seek time = better movement efficiency in this simulation.")

        st.markdown("### > EXECUTION EXPLAINER")
        _render_stepwise_explainer(state.get("last_result"))

        if st.button("> BACK TO OS DASHBOARD", use_container_width=True):
            run_layer_transition(
                "OS",
                logs=["[EXITING SUBSYSTEM]", "[SAVING STATE]", "[RETURNING TO PREVIOUS LAYER]"],
            )
            set_layer("os")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Scheduler layer fault: {exc}")
