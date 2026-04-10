"""Scheduling algorithms with safe fallbacks."""

from typing import Dict, Iterable, List

from .queue_manager import IORequest, ScheduleResult


def _safe_requests(requests: Iterable[IORequest]) -> List[IORequest]:
    try:
        return [request for request in requests if isinstance(request, IORequest)]
    except Exception:
        return []


def _build_result(name: str, ordered: List[IORequest], initial_head: int) -> ScheduleResult:
    result = ScheduleResult(algorithm=name)
    try:
        head = int(initial_head)
        current_time = 0.0
        for request in ordered:
            wait = max(0.0, current_time - request.arrival_time)
            seek = float(abs(request.track - head))
            head = request.track
            current_time += seek + request.burst_time
            result.execution_order.append(request.request_id)
            result.seek_times.append(seek)
            result.head_positions.append(head)
            result.wait_times.append(round(wait, 2))
            result.completion_times.append(round(current_time, 2))
        return result.finalize()
    except Exception:
        return result.finalize()


def run_fcfs(requests: Iterable[IORequest], initial_head: int) -> ScheduleResult:
    try:
        return _build_result("FCFS", _safe_requests(requests), initial_head)
    except Exception:
        return ScheduleResult(algorithm="FCFS").finalize()


def run_sstf(requests: Iterable[IORequest], initial_head: int) -> ScheduleResult:
    try:
        pending = _safe_requests(requests)
        ordered: List[IORequest] = []
        head = int(initial_head)
        while pending:
            next_request = min(pending, key=lambda item: abs(item.track - head))
            ordered.append(next_request)
            head = next_request.track
            pending.remove(next_request)
        return _build_result("SSTF", ordered, initial_head)
    except Exception:
        return ScheduleResult(algorithm="SSTF").finalize()


def run_scan(requests: Iterable[IORequest], initial_head: int, direction: str = "out") -> ScheduleResult:
    try:
        items = sorted(_safe_requests(requests), key=lambda item: item.track)
        lower = [item for item in items if item.track < initial_head]
        upper = [item for item in items if item.track >= initial_head]
        ordered = upper + list(reversed(lower)) if direction == "out" else list(reversed(lower)) + upper
        return _build_result("SCAN", ordered, initial_head)
    except Exception:
        return ScheduleResult(algorithm="SCAN").finalize()


def run_algorithm(name: str, requests: Iterable[IORequest], initial_head: int) -> ScheduleResult:
    try:
        selected = (name or "FCFS").upper()
        if selected == "SSTF":
            return run_sstf(requests, initial_head)
        if selected == "SCAN":
            return run_scan(requests, initial_head)
        return run_fcfs(requests, initial_head)
    except Exception:
        return ScheduleResult(algorithm="FCFS").finalize()


def compare_algorithms(requests: Iterable[IORequest], initial_head: int) -> Dict[str, ScheduleResult]:
    try:
        queue = _safe_requests(requests)
        return {
            "FCFS": run_fcfs(queue, initial_head),
            "SSTF": run_sstf(queue, initial_head),
            "SCAN": run_scan(queue, initial_head),
        }
    except Exception:
        return {}
