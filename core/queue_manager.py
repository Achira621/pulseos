"""Queue manager logic for handling state and request history."""
import time
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class IORequest:
    request_id: int
    track: int
    arrival_time: float
    priority: int = 5
    burst_time: float = 10.0
    status: str = "pending"  # pending, running, completed

@dataclass
class DiskState:
    current_head: int = 500
    direction: str = "out"  # in (towards 0), out (towards max)

@dataclass
class ScheduleResult:
    algorithm: str
    execution_order: List[int] = field(default_factory=list)
    seek_times: List[float] = field(default_factory=list)
    head_positions: List[int] = field(default_factory=list)
    wait_times: List[float] = field(default_factory=list)
    completion_times: List[float] = field(default_factory=list)
    total_seek_time: float = 0.0
    average_seek_time: float = 0.0
    total_head_movements: int = 0

    def finalize(self) -> "ScheduleResult":
        try:
            if self.seek_times:
                self.total_seek_time = float(sum(self.seek_times))
                self.average_seek_time = self.total_seek_time / len(self.seek_times)
                self.total_head_movements = len(self.seek_times)
            return self
        except Exception:
            return self

class QueueManager:
    """Manages the lifecycle of I/O requests with fault tolerance."""
    
    def __init__(self):
        self._queue: List[IORequest] = []
        self._id_counter = 0

    def add_request(self, track: int, priority: int = 5) -> Optional[IORequest]:
        """Adds a request to the queue. Uses try-except for safety."""
        try:
            self._id_counter += 1
            request = IORequest(
                request_id=self._id_counter,
                track=track,
                arrival_time=time.time(),
                priority=priority
            )
            self._queue.append(request)
            return request
        except Exception:
            return None

    def clear(self) -> bool:
        try:
            self._queue = []
            return True
        except Exception:
            return False

    def snapshot(self) -> List[IORequest]:
        """Returns a copy of the current queue."""
        try:
            return [req for req in self._queue]
        except Exception:
            return []

    def get_count(self) -> int:
        try:
            return len(self._queue)
        except Exception:
            return 0
