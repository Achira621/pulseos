"""Logic for calculating and generating system performance metrics."""
from typing import Dict, Any

def get_fake_system_snapshot(device_count: int = 0, queue_size: int = 0) -> Dict[str, float]:
    """Generates deterministic telemetry derived from state."""
    try:
        cpu = min(100.0, 15.0 + device_count * 8.0 + queue_size * 4.0)
        memory = min(100.0, 22.0 + device_count * 5.0 + queue_size * 6.0)
        disk = min(100.0, 10.0 + queue_size * 9.0 + device_count * 3.0)
        return {
            "cpu": float(round(cpu, 2)),
            "memory": float(round(memory, 2)),
            "disk": float(round(disk, 2)),
        }
    except Exception:
        return {"cpu": 0.0, "memory": 0.0, "disk": 0.0}

def calculate_result_metrics(result: Any) -> Dict[str, float]:
    """Calculates performance results from a schedule result-like object."""
    try:
        if result is None:
            return {
                "total_seek": 0.0,
                "average_seek": 0.0,
                "avg_wait": 0.0,
                "throughput": 0.0,
                "movements": 0.0,
            }

        seek_times = getattr(result, "seek_times", []) or []
        wait_times = getattr(result, "wait_times", []) or []
        completion_times = getattr(result, "completion_times", []) or []
        total = sum(seek_times) if seek_times else 0.0
        average = (total / len(seek_times)) if seek_times else 0.0
        avg_wait = (sum(wait_times) / len(wait_times)) if wait_times else 0.0
        duration = completion_times[-1] if completion_times else 0.0
        throughput = (len(seek_times) / duration) if duration else 0.0

        return {
            "total_seek": float(total),
            "average_seek": float(average),
            "avg_wait": float(avg_wait),
            "throughput": float(throughput),
            "movements": float(len(seek_times)),
        }
    except Exception:
        return {
            "total_seek": 0.0,
            "average_seek": 0.0,
            "avg_wait": 0.0,
            "throughput": 0.0,
            "movements": 0.0,
        }
