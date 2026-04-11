"""
Dedicated Algorithm Analysis Mode.
Purpose: Deep-dive panel for each scheduling algorithm (FCFS, SSTF, SCAN).
Input: Uses the same shared queue and head position from session state.
Output: Renders independent tabs per algorithm with tables, charts, and explanations.
Failure Handling: All rendering wrapped in try-except with safe fallback messages.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from core.metrics import calculate_result_metrics
from core.scheduler import compare_algorithms, run_fcfs, run_scan, run_sstf
from utils.state import get_system_state


# ─── Teaching content per algorithm ───────────────────────────────────────────

_ALGO_DEEP = {
    "FCFS": {
        "icon": "📋",
        "full_name": "First-Come, First-Served",
        "what": (
            "Requests are served in the exact order they arrived. "
            "No reordering or optimization is applied — pure arrival-time FIFO."
        ),
        "how": (
            "1. Take the first request in the queue.\n"
            "2. Move the disk head to that track.\n"
            "3. Record the seek distance (|current − next|).\n"
            "4. Repeat until the queue is empty."
        ),
        "formula": "|current_head − next_track|",
        "analogy": (
            "Like a grocery queue — whoever joined first gets served first, "
            "regardless of how far their aisle is from the cashier."
        ),
        "pros": ["✅ Simple to implement", "✅ No starvation — every request is guaranteed service", "✅ Fair in arrival-order terms"],
        "cons": ["❌ Can produce high total seek time", "❌ Does not optimize head movement", "❌ Inefficient for clustered requests"],
        "color": "#6b8f71",
    },
    "SSTF": {
        "icon": "🎯",
        "full_name": "Shortest-Seek-Time-First",
        "what": (
            "At each step, the algorithm picks the pending request that is "
            "closest to the current head position, minimizing immediate seek distance."
        ),
        "how": (
            "1. Compute |current_head − track| for every pending request.\n"
            "2. Choose the request with the smallest distance.\n"
            "3. Move head there, record seek distance.\n"
            "4. Repeat greedy selection until queue is empty."
        ),
        "formula": "min( |current_head − requestᵢ.track| ) for all pending requests",
        "analogy": (
            "Like a cab driver who always picks up the nearest passenger, "
            "ignoring passengers waiting far away."
        ),
        "pros": ["✅ Reduces average seek time", "✅ Efficient for clustered workloads", "✅ Better than FCFS in most benchmarks"],
        "cons": ["❌ Starvation risk — distant requests may wait indefinitely", "❌ Greedy; not globally optimal", "❌ Unpredictable service order"],
        "color": "#8f7a6b",
    },
    "SCAN": {
        "icon": "🔄",
        "full_name": "SCAN (Elevator Algorithm)",
        "what": (
            "The head sweeps in one direction servicing all requests in its path, "
            "then reverses and services the remaining requests on the return sweep."
        ),
        "how": (
            "1. Sort all requests by track number.\n"
            "2. Service requests in ascending order (outer direction).\n"
            "3. After reaching the highest request, reverse direction.\n"
            "4. Service remaining requests in descending order."
        ),
        "formula": "Sorted ascending → then reversed (elevator sweep)",
        "analogy": (
            "Like an elevator that goes up servicing all floors, "
            "then comes back down servicing those it missed — predictable and fair."
        ),
        "pros": ["✅ Prevents starvation", "✅ Predictable, bounded wait time", "✅ Good balance of performance and fairness"],
        "cons": ["❌ Requests at edges may wait for full sweep", "❌ Slightly more complex to implement", "❌ May travel unnecessarily to track ends"],
        "color": "#6b7f8f",
    },
}


# ─── Per-algorithm panel renderer ─────────────────────────────────────────────

def _render_algo_panel(algo_name: str, result, initial_head: int, queue: list = None) -> None:
    """
    Purpose: Render a full deep-dive panel for a single algorithm.
    Input: algo_name (str), result (ScheduleResult), initial_head (int), queue (list[IORequest]).
    Output: Streamlit UI components with table, graph, queue state, Gantt, and explanation.
    Failure Handling: Each section wrapped independently; degrades gracefully.
    """
    if queue is None:
        queue = []
    info = _ALGO_DEEP.get(algo_name, _ALGO_DEEP["FCFS"])
    color = info["color"]

    st.markdown(
        f"<div style='border-left: 3px solid {color}; padding-left: 12px; margin-bottom: 16px;'>"
        f"<h4 style='color:{color}; font-family: Courier New;'>"
        f"{info['icon']} {algo_name} — {info['full_name']}</h4>"
        f"<p style='color:#a0a0a0; font-size:0.85rem;'>{info['what']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.1, 1])

    # ── Execution table ───────────────────────────────────────────────────────
    with left_col:
        try:
            st.markdown("##### 📊 Execution Step Table")
            if not result or not result.execution_order:
                st.info("Run the simulation from the queue panel first to populate steps.")
            else:
                positions = [initial_head] + result.head_positions
                cumulative = 0.0
                rows = []
                for idx, req_id in enumerate(result.execution_order):
                    seek = result.seek_times[idx] if idx < len(result.seek_times) else 0.0
                    cumulative += seek
                    rows.append({
                        "Step": idx + 1,
                        "Req ID": req_id,
                        "From": int(positions[idx]),
                        "To (Track)": int(positions[idx + 1]),
                        "Seek Dist.": int(seek),
                        "Cumulative": int(cumulative),
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)
                metrics = calculate_result_metrics(result)
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Seek", int(metrics["total_seek"]))
                m2.metric("Avg Seek", round(metrics["average_seek"], 1))
                m3.metric("Steps", int(metrics["movements"]))
        except Exception:
            st.caption("Execution table unavailable.")

    # ── Movement graph ────────────────────────────────────────────────────────
    with right_col:
        try:
            st.markdown("##### 📈 Head Movement Graph")
            if not result or not result.head_positions:
                st.info("Graph will appear after execution.")
            else:
                positions = [initial_head] + result.head_positions
                steps = list(range(len(positions)))
                fig = go.Figure()
                # Shaded area under path
                fig.add_trace(go.Scatter(
                    x=steps,
                    y=positions,
                    mode="lines+markers+text",
                    line=dict(color=color, width=2.5),
                    marker=dict(size=9, color=color, symbol="circle"),
                    text=[str(p) for p in positions],
                    textposition="top center",
                    textfont=dict(size=9, color="#d6d6d6"),
                    fill="tozeroy",
                    fillcolor=color.replace("#", "rgba(").replace("6b8f71", "107,143,113,0.08")
                        .replace("8f7a6b", "143,122,107,0.08")
                        .replace("6b7f8f", "107,127,143,0.08") + ")",
                    name="Head Path",
                ))
                # Mark start
                fig.add_trace(go.Scatter(
                    x=[0], y=[initial_head],
                    mode="markers+text",
                    marker=dict(size=14, color="#d4c56a", symbol="star"),
                    text=["START"],
                    textposition="top center",
                    textfont=dict(size=9),
                    name="Start",
                    showlegend=False,
                ))
                fig.update_layout(
                    xaxis_title="Step",
                    yaxis_title="Track Position",
                    template="plotly_dark",
                    height=280,
                    margin=dict(l=20, r=20, t=20, b=30),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Courier New", size=10, color="#d6d6d6"),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Movement graph unavailable.")

    # ── Teaching explanation ──────────────────────────────────────────────────
    try:
        with st.expander(f"📖 How {algo_name} Works — Teaching Notes", expanded=False):
            exp_left, exp_right = st.columns(2)
            with exp_left:
                st.markdown("**Step-by-Step Logic:**")
                st.code(info["how"], language="text")
                st.markdown("**Service Formula:**")
                st.code(info["formula"], language="text")
            with exp_right:
                st.markdown("**Real-World Analogy:**")
                st.info(f"💡 {info['analogy']}")
                st.markdown("**Pros:**")
                for p in info["pros"]:
                    st.markdown(f"<span style='color:#6b8f71'>{p}</span>", unsafe_allow_html=True)
                st.markdown("**Cons:**")
                for c in info["cons"]:
                    st.markdown(f"<span style='color:#8f5a5a'>{c}</span>", unsafe_allow_html=True)
    except Exception:
        pass

    # ── Queue state visualizer (NEW) ──────────────────────────────────────────
    _render_queue_state(algo_name, result, queue, color)

    # ── Gantt chart (NEW) ─────────────────────────────────────────────────────
    _render_gantt_chart(algo_name, result, queue, color)


# ─── Gantt chart ─────────────────────────────────────────────────────────────

def _render_gantt_chart(algo_name: str, result, queue, color: str) -> None:
    """
    Purpose: Render a Gantt-style timeline showing when each I/O request is serviced.
    Input: algo_name (str), result (ScheduleResult), queue (list[IORequest]), color (str).
    Output: Plotly horizontal bar chart — X=time, Y=Request ID.
    Failure Handling: Wrapped in try-except; shows caption on failure.
    """
    try:
        st.markdown("##### 📅 Gantt Chart — Request Service Timeline")
        if not result or not result.execution_order:
            st.info("Gantt chart will appear after the algorithm runs.")
            return

        # Build a lookup: request_id -> arrival_time
        arrival_map = {req.request_id: getattr(req, "arrival_time", 0.0) for req in queue}

        bars = []
        for idx, req_id in enumerate(result.execution_order):
            seek = result.seek_times[idx] if idx < len(result.seek_times) else 0.0
            burst = 0.0
            for req in queue:
                if req.request_id == req_id:
                    burst = getattr(req, "burst_time", 10.0)
                    break
            start_t = result.completion_times[idx] - seek - burst if idx < len(result.completion_times) else 0.0
            end_t = result.completion_times[idx] if idx < len(result.completion_times) else start_t + seek + burst
            bars.append({
                "ReqID": f"Req #{req_id}",
                "Start": round(start_t, 2),
                "Finish": round(end_t, 2),
                "Seek": round(seek, 2),
                "Burst": round(burst, 2),
                "Step": idx + 1,
            })

        fig = go.Figure()
        bar_colors = [color, "#8f7a6b", "#6b7f8f", "#8f6b8f", "#7f8f6b"]
        for i, bar in enumerate(bars):
            duration = bar["Finish"] - bar["Start"]
            fig.add_trace(go.Bar(
                x=[duration],
                y=[bar["ReqID"]],
                orientation="h",
                base=bar["Start"],
                marker=dict(
                    color=bar_colors[i % len(bar_colors)],
                    opacity=0.85,
                    line=dict(color="#1a1a1a", width=1),
                ),
                text=f"Step {bar['Step']} | Seek:{bar['Seek']} Burst:{bar['Burst']}",
                textposition="inside",
                textfont=dict(size=9, color="#d6d6d6"),
                name=bar["ReqID"],
                showlegend=False,
                hovertemplate=(
                    f"<b>{bar['ReqID']}</b><br>"
                    f"Start: {bar['Start']}<br>"
                    f"End: {bar['Finish']}<br>"
                    f"Seek: {bar['Seek']} | Burst: {bar['Burst']}<extra></extra>"
                ),
            ))

        fig.update_layout(
            xaxis_title="Time (seek + burst)",
            yaxis_title="Request",
            yaxis=dict(autorange="reversed"),
            template="plotly_dark",
            height=max(220, 40 + len(bars) * 36),
            margin=dict(l=20, r=20, t=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Courier New", size=10, color="#d6d6d6"),
            bargap=0.25,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each bar = one request. Width = seek time + burst time. Left-edge = service start.")
    except Exception:
        st.caption("Gantt chart unavailable.")


# ─── Queue state visualizer ───────────────────────────────────────────────────

def _render_queue_state(algo_name: str, result, queue, color: str) -> None:
    """
    Purpose: Show all requests on the track axis, colored by service order for this algorithm.
    Input: algo_name (str), result (ScheduleResult), queue (list[IORequest]), color (str).
    Output: Plotly scatter — X=track, colored by order served (green=early, red=late).
    Failure Handling: Wrapped in try-except; shows caption on failure.
    """
    try:
        st.markdown("##### 🗂️ Queue State — Track Distribution & Service Order")
        if not queue:
            st.info("No requests in queue.")
            return

        # Build service-order map for this algorithm
        order_map = {}
        if result and result.execution_order:
            for step, req_id in enumerate(result.execution_order):
                order_map[req_id] = step + 1

        tracks, ids, orders, labels, priorities = [], [], [], [], []
        for req in queue:
            tracks.append(req.track)
            ids.append(req.request_id)
            step = order_map.get(req.request_id, 0)
            orders.append(step)
            priorities.append(getattr(req, "priority", 5))
            label = f"Req #{req.request_id}\nTrack:{req.track}\nServed: Step {step}" if step else f"Req #{req.request_id}\nTrack:{req.track}"
            labels.append(label)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tracks,
            y=[0] * len(tracks),
            mode="markers+text",
            marker=dict(
                size=[max(10, p * 3) for p in priorities],
                color=orders if orders else [0] * len(tracks),
                colorscale=[[0, "#3a3a3a"], [0.5, color], [1.0, "#d4c56a"]],
                showscale=True,
                colorbar=dict(
                    title="Serve Order",
                    thickness=10,
                    len=0.6,
                    tickfont=dict(size=8, color="#d6d6d6"),
                    titlefont=dict(size=9, color="#d6d6d6"),
                ),
                line=dict(color="#333", width=1),
                symbol="circle",
            ),
            text=[f"#{r}" for r in ids],
            textposition="top center",
            textfont=dict(size=9, color="#d6d6d6"),
            customdata=labels,
            hovertemplate="%{customdata}<extra></extra>",
            name="Requests",
        ))
        # Horizontal axis line for visual clarity
        fig.add_hline(y=0, line=dict(color="#333", width=1, dash="dot"))

        fig.update_layout(
            xaxis_title="Disk Track Number",
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.5, 0.8]),
            template="plotly_dark",
            height=180,
            margin=dict(l=20, r=60, t=10, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Courier New", size=10, color="#d6d6d6"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Dot size = priority. Color = service order (brighter = served later). Darker = served earlier.")
    except Exception:
        st.caption("Queue state chart unavailable.")


# ─── Summary comparison bar ───────────────────────────────────────────────────

def _render_dedicated_summary(results: dict, initial_head: int) -> None:
    """
    Purpose: Render bottom summary table + bar chart comparing all three algorithms.
    Input: results dict {algo_name: ScheduleResult}, initial_head for reference.
    Output: Comparison section matching Unified Mode output.
    Failure Handling: Returns silently if results are empty.
    """
    try:
        if not results:
            return
        st.markdown("---")
        st.markdown("### > CROSS-ALGORITHM SUMMARY  *(matches Unified Mode)*")
        st.caption(f"All algorithms ran on the same queue with head starting at track **{initial_head}**.")

        algo_names, total_seeks, avg_seeks = [], [], []
        rows = []
        for algo_name, result in results.items():
            if result:
                metrics = calculate_result_metrics(result)
                algo_names.append(algo_name)
                total_seeks.append(round(metrics["total_seek"], 2))
                avg_seeks.append(round(metrics["average_seek"], 2))
                rows.append({
                    "Algorithm": algo_name,
                    "Total Seek": round(metrics["total_seek"], 2),
                    "Avg Seek": round(metrics["average_seek"], 2),
                    "Steps": int(metrics["movements"]),
                })

        if not rows:
            st.info("Add requests and run an algorithm to see the summary.")
            return

        fig = go.Figure()
        colors = ["#6b8f71", "#8f7a6b", "#6b7f8f"]
        for i, (name, total, avg) in enumerate(zip(algo_names, total_seeks, avg_seeks)):
            fig.add_trace(go.Bar(
                name=name,
                x=["Total Seek", "Avg Seek"],
                y=[total, avg],
                marker_color=colors[i % len(colors)],
                text=[str(total), str(avg)],
                textposition="outside",
            ))
        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Courier New", size=10, color="#d6d6d6"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("Lower seek values = better movement efficiency.")
    except Exception:
        st.caption("Summary comparison unavailable.")


# ─── Main entry point ─────────────────────────────────────────────────────────

def render_dedicated_algo_view() -> None:
    """
    Purpose: Render the full Dedicated Algorithm Analysis Mode.
    Input: Reads shared queue and head position from session state.
    Output: Three algorithm tabs (FCFS, SSTF, SCAN) + bottom summary.
    Failure Handling: Top-level except renders an error banner.
    """
    try:
        state = get_system_state()
        queue = state.get("io_queue", [])
        initial_head = int(state.get("current_head", 500))

        st.markdown(
            "<div style='border-bottom: 1px solid #333; margin-bottom:12px; padding-bottom:6px;'>"
            "<span style='color:#6b8f71; font-family: Courier New; font-size:0.8rem;'>"
            "[DEDICATED ANALYSIS MODE] — using same queue as Unified Mode</span></div>",
            unsafe_allow_html=True,
        )

        if not queue:
            st.warning("Queue is empty. Add I/O requests in Unified Mode first, then switch here to analyse.")
            return

        # Run all three algorithms on the shared queue + head
        try:
            results = compare_algorithms(queue, initial_head)
        except Exception:
            results = {}

        tab_fcfs, tab_sstf, tab_scan = st.tabs([
            "📋  FCFS",
            "🎯  SSTF",
            "🔄  SCAN",
        ])

        with tab_fcfs:
            _render_algo_panel("FCFS", results.get("FCFS"), initial_head, queue)

        with tab_sstf:
            _render_algo_panel("SSTF", results.get("SSTF"), initial_head, queue)

        with tab_scan:
            _render_algo_panel("SCAN", results.get("SCAN"), initial_head, queue)

        _render_dedicated_summary(results, initial_head)

    except Exception as exc:
        st.error(f"Dedicated analysis fault: {exc}")
