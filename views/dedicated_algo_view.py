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

def _render_algo_panel(algo_name: str, result, initial_head: int) -> None:
    """
    Purpose: Render a full deep-dive panel for a single algorithm.
    Input: algo_name (str), result (ScheduleResult), initial_head (int).
    Output: Streamlit UI components with table, graph, and explanation.
    Failure Handling: Each section wrapped independently; degrades gracefully.
    """
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
            _render_algo_panel("FCFS", results.get("FCFS"), initial_head)

        with tab_sstf:
            _render_algo_panel("SSTF", results.get("SSTF"), initial_head)

        with tab_scan:
            _render_algo_panel("SCAN", results.get("SCAN"), initial_head)

        _render_dedicated_summary(results, initial_head)

    except Exception as exc:
        st.error(f"Dedicated analysis fault: {exc}")
