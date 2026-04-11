"""Scheduler execution layer with teaching overlays and comparison."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

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
from views.dedicated_algo_view import render_dedicated_algo_view

ALGO_NOTES = {
    "FCFS": {
        "what": "Serves requests in arrival order.",
        "why": "Simple and fair for basic scheduling demonstration.",
        "logic": "Process queue from first to last.",
        "pros": "Easy to implement, no starvation in simple queues.",
        "cons": "Can produce high seek movement.",
        "analogy": "Like a checkout line at a grocery store - first come, first served.",
    },
    "SSTF": {
        "what": "Picks the request closest to current head position.",
        "why": "Usually reduces total seek time.",
        "logic": "Choose minimum |current_head - request_track| repeatedly.",
        "pros": "Fast average seek behavior.",
        "cons": "Far requests may wait too long (starvation risk).",
        "analogy": "Like a delivery driver making stops at the closest house next, avoiding driving back and forth.",
    },
    "SCAN": {
        "what": "Moves head in one direction servicing tracks, then reverses.",
        "why": "Balances fairness and performance.",
        "logic": "Sort requests by track and traverse like an elevator.",
        "pros": "Predictable and fairer than SSTF.",
        "cons": "Can still travel long distances at queue edges.",
        "analogy": "Like an elevator picking up passengers while traveling up, then doing the same on the way down.",
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
            
        # Plotly chart for head movement
        steps = list(range(len(result.head_positions)))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=result.head_positions,
            y=steps,
            mode='lines+markers+text',
            line=dict(color='#00ffcc', width=3),
            marker=dict(size=10, color='#ff00ff', symbol='diamond'),
            text=[str(p) for p in result.head_positions],
            textposition="top center",
            name='Head Path'
        ))
        
        # Reverse Y axis so step 0 is at the top
        max_x = max(result.head_positions) if result.head_positions else 200
        fig.update_layout(
            title="Disk Head Movement Path",
            xaxis_title="Track Number",
            yaxis_title="Step Sequence",
            yaxis=dict(autorange="reversed", tickmode="linear"),
            xaxis=dict(range=[0, max_x + 50]),
            template="plotly_dark",
            margin=dict(l=40, r=40, t=40, b=40),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

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

def _render_dedicated_panel(algo_name: str, result) -> None:
    notes = ALGO_NOTES.get(algo_name, {})
    
    st.markdown(f"#### {algo_name} Focus View")
    st.info(f"**What it does:** {notes.get('what', '')}\n\n**Logic:** {notes.get('logic', '')}\n\n**Analogy:** {notes.get('analogy', '')}")
    col_pros, col_cons = st.columns(2)
    with col_pros:
        st.success(f"**Pros:** {notes.get('pros', '')}")
    with col_cons:
        st.warning(f"**Cons:** {notes.get('cons', '')}")
        
    if not result or not result.execution_order:
        st.caption("Add requests to the queue to see simulation.")
        return
        
    num_steps = len(result.head_positions)
    st.markdown("#### Live Simulation")
    
    # Control Live Simulation
    step_idx = st.slider(f"{algo_name} Simulation Step", min_value=0, max_value=num_steps, value=num_steps, key=f"slider_{algo_name}")
    
    if step_idx > 0:
        c1, c2 = st.columns([1, 1])
        with c1:
            rows = []
            cumulative_time = 0
            for idx in range(step_idx):
                cumulative_time += result.seek_times[idx]
                rows.append({
                    "Step": idx + 1,
                    "Head Pos": result.head_positions[idx],
                    "Target ID": result.execution_order[idx],
                    "Seek Dist": round(result.seek_times[idx], 2),
                    "Total Time": round(result.completion_times[idx], 2)
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)
            
        with c2:
            steps = list(range(step_idx))
            x_data = result.head_positions[:step_idx]
            
            fig = go.Figure()
            # Full path faint
            fig.add_trace(go.Scatter(
                x=result.head_positions,
                y=list(range(num_steps)),
                mode='lines',
                line=dict(color='rgba(255,255,255,0.1)', width=1, dash='dot'),
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Simulated path
            fig.add_trace(go.Scatter(
                x=x_data,
                y=steps,
                mode='lines+markers+text',
                line=dict(color='#00ffcc', width=3),
                marker=dict(size=10, color='#ff00ff', symbol='diamond'),
                text=[str(p) for p in x_data],
                textposition="top center",
                name='Simulated Path'
            ))
            
            max_x = max(result.head_positions) if result.head_positions else 200
            fig.update_layout(
                title=f"Path execution up to Step {step_idx}/{num_steps}",
                xaxis_title="Track Number",
                yaxis_title="Step Sequence",
                yaxis=dict(autorange="reversed", tickmode="linear"),
                xaxis=dict(range=[0, max_x + 50]),
                template="plotly_dark",
                margin=dict(l=40, r=40, t=40, b=40),
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Move the slider to start the simulation.")

def _render_per_device_queues(queue: list, device_names: list) -> None:
    """
    Purpose: Show individual device queues filtered from the master io_queue.
    Input: queue (list[IORequest]), device_names (list[str]).
    Output: One expander per connected device showing its pending requests + mini scatter.
    Failure Handling: Wrapped in try-except; skips devices silently on error.
    """
    try:
        st.markdown("### > INDIVIDUAL DEVICE QUEUES")
        st.caption("Each connected device's pending I/O requests, filtered from the unified queue.")
        if not device_names:
            st.info("No devices connected.")
            return
        for dev in device_names:
            dev_reqs = [req for req in queue if getattr(req, "target_device", "") == dev]
            badge = f"({len(dev_reqs)} request{'s' if len(dev_reqs) != 1 else ''})"
            with st.expander(f"📦 {dev}  {badge}", expanded=len(dev_reqs) > 0):
                if not dev_reqs:
                    st.caption("No pending requests for this device.")
                    continue
                rows = [
                    {
                        "ID": r.request_id,
                        "Track": r.track,
                        "Priority": r.priority,
                        "Burst": r.burst_time,
                    }
                    for r in dev_reqs
                ]
                st.dataframe(rows, use_container_width=True, hide_index=True)
                # Mini track scatter
                try:
                    tracks = [r.track for r in dev_reqs]
                    ids    = [r.request_id for r in dev_reqs]
                    prios  = [r.priority for r in dev_reqs]
                    fig = go.Figure(go.Scatter(
                        x=tracks,
                        y=[0] * len(tracks),
                        mode="markers+text",
                        marker=dict(
                            size=[max(8, p * 3) for p in prios],
                            color=prios,
                            colorscale="Viridis",
                            showscale=False,
                            line=dict(color="#333", width=1),
                        ),
                        text=[f"#{i}" for i in ids],
                        textposition="top center",
                        textfont=dict(size=9, color="#d6d6d6"),
                    ))
                    fig.update_layout(
                        xaxis_title="Track",
                        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.6, 0.8]),
                        template="plotly_dark",
                        height=130,
                        margin=dict(l=20, r=20, t=6, b=30),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Courier New", size=9, color="#d6d6d6"),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass
    except Exception:
        st.caption("Per-device queue view unavailable.")


def _render_gantt_unified(result, queue: list) -> None:
    """
    Purpose: Render a Gantt chart in the Unified Scheduler after algorithm execution.
    Input: result (ScheduleResult), queue (list[IORequest]).
    Output: Horizontal bar Gantt — Y=Request, X=time axis showing seek + burst segments.
    Failure Handling: Wrapped in try-except; shows caption on failure.
    """
    try:
        st.markdown("### > GANTT CHART — Scheduling Timeline")
        st.caption("Each bar = one I/O request. Left segment = seek time (head travel). Right segment = burst time (service). Total width = completion span.")
        if not result or not result.execution_order:
            st.info("Run an algorithm to see the Gantt chart.")
            return

        burst_map = {req.request_id: getattr(req, "burst_time", 10.0) for req in queue}

        fig = go.Figure()
        SEEK_COLOR  = "#6b8f71"
        BURST_COLOR = "#8f7a6b"

        for idx, req_id in enumerate(result.execution_order):
            seek  = result.seek_times[idx]  if idx < len(result.seek_times)  else 0.0
            comp  = result.completion_times[idx] if idx < len(result.completion_times) else 0.0
            burst = burst_map.get(req_id, 10.0)
            service_start = comp - burst
            seek_start    = service_start - seek
            label = f"Req #{req_id}"

            # Seek segment (head travel)
            fig.add_trace(go.Bar(
                x=[seek],
                y=[label],
                orientation="h",
                base=seek_start,
                name="Seek" if idx == 0 else "",
                showlegend=idx == 0,
                marker=dict(color=SEEK_COLOR, opacity=0.75, line=dict(color="#1a1a1a", width=1)),
                hovertemplate=f"<b>{label}</b><br>Seek: {round(seek,2)}<br>Start: {round(seek_start,2)}<extra></extra>",
                text=f"seek {round(seek,1)}",
                textposition="inside",
                textfont=dict(size=8, color="#d6d6d6"),
            ))
            # Burst segment (I/O service)
            fig.add_trace(go.Bar(
                x=[burst],
                y=[label],
                orientation="h",
                base=service_start,
                name="Burst" if idx == 0 else "",
                showlegend=idx == 0,
                marker=dict(color=BURST_COLOR, opacity=0.85, line=dict(color="#1a1a1a", width=1)),
                hovertemplate=f"<b>{label}</b><br>Burst: {round(burst,2)}<br>Done @: {round(comp,2)}<extra></extra>",
                text=f"burst {round(burst,1)}",
                textposition="inside",
                textfont=dict(size=8, color="#d6d6d6"),
            ))

        fig.update_layout(
            barmode="overlay",
            xaxis_title="Time (cumulative seek + burst)",
            yaxis_title="Request",
            yaxis=dict(autorange="reversed"),
            template="plotly_dark",
            height=max(260, 50 + len(result.execution_order) * 38),
            margin=dict(l=20, r=20, t=10, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Courier New", size=10, color="#d6d6d6"),
            bargap=0.3,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True)
        # Summary row
        if result.completion_times:
            total_span = result.completion_times[-1]
            st.caption(f"Total scheduling span: **{round(total_span, 2)}** time units  |  "
                       f"🟩 Green = seek (head travel)  |  🟫 Amber = burst (I/O service)")
    except Exception:
        st.caption("Gantt chart unavailable.")


def _render_performance_summary(results) -> None:
    algo_names = []
    total_seeks = []
    avg_seeks = []
    
    rows = []
    for algo_name, result in results.items():
        if not result.execution_order:
            continue
        stats = calculate_result_metrics(result)
        algo_names.append(algo_name)
        total_seeks.append(round(stats["total_seek"], 2))
        avg_seeks.append(round(stats["average_seek"], 2))
        
        rows.append(
            {
                "Algorithm": algo_name,
                "Total Seek Time": round(stats["total_seek"], 2),
                "Avg Seek Time": round(stats["average_seek"], 2),
            }
        )
        
    if not rows:
        st.caption("No requests to calculate performance.")
        return
        
    c1, c2 = st.columns([1, 1])
    with c1:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with c2:
        fig = px.bar(
            x=algo_names, 
            y=total_seeks, 
            text=total_seeks,
            labels={'x': 'Algorithm', 'y': 'Total Seek Time'},
            title="Total Seek Time Comparison",
            template="plotly_dark",
            color=algo_names,
            color_discrete_sequence=['#00ffcc', '#ff00ff', '#ffff00']
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)


def render_scheduler_view() -> None:
    """
    Purpose: Top-level scheduler entry point — presents Unified / Dedicated mode tabs.
    Input: None (reads from session state).
    Output: Renders selected mode.
    Failure Handling: Falls back to unified on error.
    """
    try:
        mode_tab_unified, mode_tab_dedicated = st.tabs([
            "⚡  Unified Mode",
            "🔬  Dedicated Analysis Mode",
        ])
        with mode_tab_unified:
            _render_unified_scheduler_impl()
        with mode_tab_dedicated:
            render_dedicated_algo_view()
    except Exception as exc:
        st.error(f"Mode switch fault: {exc}")


def _render_unified_scheduler_impl() -> None:
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
            if add_io_request(int(track), int(priority), float(burst), target_device):
                st.success(f"{target_device} request added at track {int(track)}.")
                st.rerun()
            else:
                st.error("Failed to add request.")
        if a2.button("REMOVE LAST REQUEST", use_container_width=True):
            if queue and remove_io_request(queue[-1].request_id):
                st.success("Last request removed.")
                st.rerun()
            else:
                st.info("No removable request found in queue.")
        if a3.button("CLEAR QUEUE", use_container_width=True):
            clear_io_queue()
            st.rerun()

        st.markdown("### > UNIFIED I/O QUEUE")
        if queue:
            st.markdown("#### Queue Details")
            st.dataframe(
                [{"ID": req.request_id, "Target Device": getattr(req, "target_device", "Unknown"), "Logical Track/Address": req.track, "Priority": req.priority, "Burst": req.burst_time} for req in queue],
                use_container_width=True,
                hide_index=True,
            )
            
            # Queue distribution visualization
            tracks = [req.track for req in queue]
            priorities = [req.priority for req in queue]
            ids = [req.request_id for req in queue]
            
            fig_queue = px.scatter(
                x=tracks,
                y=[0] * len(tracks), # 1D plot
                size=[max(1, p * 3) for p in priorities], 
                color=priorities,
                text=ids,
                title="Universal Queue Scatter (Track/Address vs Priority)",
                labels={'x': 'Logical Track/Address', 'y': ''},
                template="plotly_dark",
                color_continuous_scale="Viridis"
            )
            fig_queue.update_traces(textposition='top center', marker=dict(symbol='circle', opacity=0.8))
            fig_queue.update_layout(
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                height=220, 
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_queue, use_container_width=True)

        # Per-device individual queues (NEW)
        _render_per_device_queues(queue, device_names)

        use_priority = st.checkbox("Apply priority sorting before algorithm", value=False)
        execution_queue = _priority_sorted(queue) if use_priority else list(queue)

        st.markdown("### > SCHEDULER VIEW MODES")
        mode = st.radio("Mode Selection", ["Unified Mode", "Dedicated Mode"], horizontal=True, label_visibility="collapsed")
        st.divider()

        if mode == "Unified Mode":
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
            
            st.info(f"**What it does:** {notes['what']}\n\n**Why used:** {notes['why']}")
            
            col_pros, col_cons = st.columns(2)
            with col_pros:
                st.success(f"**Pros:** {notes['pros']}")
            with col_cons:
                st.warning(f"**Cons:** {notes['cons']}")
                
            with st.expander("Show Logic Pseudo-code"):
                st.code(notes["logic"], language="text")

            run_col, compare_col = st.columns(2)
            if run_col.button("RUN SELECTED ALGORITHM", use_container_width=True):
                if not queue:
                    st.error("Unified I/O queue is empty. Cannot execute scheduling.")
                else:
                    result = run_algorithm(current_algo, execution_queue, state["current_head"])
                    state["last_result"] = result
                    if result.head_positions:
                        state["current_head"] = result.head_positions[-1]
                    state["device_event_log"].append(f"[SERVICE] Unified Queue -> {result.execution_order}")
                    st.success("Execution complete.")

            if compare_col.button("COMPARE FCFS / SSTF / SCAN", use_container_width=True):
                if not queue:
                    st.warning("Queue empty. Add requests for comparison.")
                else:
                    results = compare_algorithms(execution_queue, state["current_head"])
                    
                    algo_names = []
                    total_seeks = []
                    avg_seeks = []
                    
                    rows = []
                    for algo_name, result in results.items():
                        stats = calculate_result_metrics(result)
                        algo_names.append(algo_name)
                        total_seeks.append(round(stats["total_seek"], 2))
                        avg_seeks.append(round(stats["average_seek"], 2))
                        
                        rows.append(
                            {
                                "Algorithm": algo_name,
                                "Order": str(result.execution_order),
                                "Total Time": round(stats["total_seek"], 2),
                                "Avg Time": round(stats["average_seek"], 2),
                            }
                        )
                    st.markdown("#### Performance Comparison")
                    
                    # Bar chart for Total Seek Time
                    fig = px.bar(
                        x=algo_names, 
                        y=total_seeks, 
                        text=total_seeks,
                        labels={'x': 'Algorithm', 'y': 'Total Seek Time'},
                        title="Total Seek Time Comparison",
                        template="plotly_dark",
                        color=algo_names,
                        color_discrete_sequence=['#00ffcc', '#ff00ff', '#ffff00']
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                    st.caption("Lower total seek time = better movement efficiency in this simulation.")

            st.markdown("### > EXECUTION EXPLAINER")
            _render_stepwise_explainer(state.get("last_result"))

            # Gantt chart after algorithm runs (NEW)
            _render_gantt_unified(state.get("last_result"), queue)
            
        elif mode == "Dedicated Mode":
            st.markdown("### > DEDICATED ALGORITHM ANALYSIS")
            st.caption("Deep-dive visualization for individual algorithms simulating from current head position.")
            
            results = compare_algorithms(execution_queue, state["current_head"])
            algo_tabs = st.tabs(["FCFS", "SSTF", "SCAN"])
            
            for i, algo in enumerate(["FCFS", "SSTF", "SCAN"]):
                with algo_tabs[i]:
                    _render_dedicated_panel(algo, results.get(algo))
                    
            st.divider()
            st.markdown("### > ALGORITHM PERFORMANCE LINKS")
            _render_performance_summary(results)

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
