"""Shared persistent simulation state for all layers."""

from typing import Dict, List

import streamlit as st

from config import DEFAULT_HEAD
from core.queue_manager import IORequest

DEVICE_CATALOG = [
    "Keyboard",
    "Mouse",
    "Printer",
    "Disk Drive",
    "USB Drive",
    "Network Interface Card (NIC)",
    "Scanner",
    "Speaker",
    "DMA Controller",
    "Interrupt Controller",
    "IO Port Bus",
    "SATA Controller",
    "GPU",
    "Touch Controller",
    "Serial Port (COM)",
    "Parallel Port (LPT)",
]


def init_system_state() -> Dict[str, object]:
    """Initializes the global state object once per session."""
    try:
        if "system_state" not in st.session_state:
            st.session_state["system_state"] = {
                "connected_devices": [],
                "io_queue": [],
                "current_head": DEFAULT_HEAD,
                "active_algorithm": "FCFS",
                "current_layer": "physical",
                "request_counter": 0,
                "last_result": None,
                "transition_log": [],
                "device_event_log": [],
                "device_queues": {},
            }
        return st.session_state["system_state"]
    except Exception:
        return {
            "connected_devices": [],
            "io_queue": [],
            "current_head": DEFAULT_HEAD,
            "active_algorithm": "FCFS",
            "current_layer": "physical",
            "request_counter": 0,
            "last_result": None,
            "transition_log": [],
            "device_event_log": [],
            "device_queues": {},
        }


def get_system_state() -> Dict[str, object]:
    try:
        return init_system_state()
    except Exception:
        return init_system_state()


def set_layer(layer: str) -> None:
    try:
        state = init_system_state()
        state["current_layer"] = layer
    except Exception:
        return


def connect_device(name: str) -> bool:
    """Marks a catalog device as plugged and keeps it STANDBY until initialized."""
    try:
        state = init_system_state()
        devices: List[dict] = state["connected_devices"]
        if any(device.get("name") == name for device in devices):
            return False
        devices.append({"name": name, "status": "INITIALIZING", "plugged": True})
        if name not in state["device_queues"]:
            state["device_queues"][name] = []
        state["device_event_log"].append(f"[DEVICE DETECTED] {name}")
        return True
    except Exception:
        return False


def initialize_connected_devices() -> None:
    try:
        state = init_system_state()
        for device in state["connected_devices"]:
            device["status"] = "READY"
            name = device.get("name", "Unknown")
            state["device_event_log"].append(f"[DRIVER LOADED] {name}")
            state["device_event_log"].append(f"[INTERRUPT REGISTERED] {name}")
    except Exception:
        return


def add_io_request(track: int, priority: int, burst_time: float = 10.0, target_device: str = "Disk Drive") -> bool:
    try:
        state = init_system_state()
        state["request_counter"] += 1
        request = IORequest(
            request_id=state["request_counter"],
            track=int(track),
            arrival_time=float(state["request_counter"]),
            priority=int(priority),
            burst_time=float(burst_time),
            target_device=target_device
        )
        state["io_queue"].append(request)
        state["device_event_log"].append(f"[QUEUE UPDATE] Universal I/O Queue <- {target_device} at track {int(track)}")
        return True
    except Exception:
        return False


def add_device_request(device_name: str, payload: str) -> bool:
    """Adds a generic request entry for non-disk I/O endpoints."""
    try:
        state = init_system_state()
        state["request_counter"] += 1
        if device_name not in state["device_queues"]:
            state["device_queues"][device_name] = []
        state["device_queues"][device_name].append(f"{payload}-R{state['request_counter']}")
        state["device_event_log"].append(f"[QUEUE UPDATE] {device_name} <- {payload}")
        return True
    except Exception:
        return False


def pop_last_device_request(device_name: str) -> bool:
    try:
        state = init_system_state()
        queue = state["device_queues"].get(device_name, [])
        if not queue:
            return False
        queue.pop()
        return True
    except Exception:
        return False


def get_connected_device_names() -> List[str]:
    try:
        state = init_system_state()
        return [device.get("name", "Unknown") for device in state["connected_devices"]]
    except Exception:
        return []


def reset_system() -> None:
    try:
        st.session_state["system_state"] = {
            "connected_devices": [],
            "io_queue": [],
            "current_head": DEFAULT_HEAD,
            "active_algorithm": "FCFS",
            "current_layer": "physical",
            "request_counter": 0,
            "last_result": None,
            "transition_log": [],
            "device_event_log": [],
            "device_queues": {},
        }
    except Exception:
        return


def remove_io_request(request_id: int) -> bool:
    try:
        state = init_system_state()
        before = len(state["io_queue"])
        removed_track = None
        filtered = []
        for req in state["io_queue"]:
            if req.request_id == int(request_id) and removed_track is None:
                removed_track = req.track
                continue
            filtered.append(req)
        state["io_queue"] = filtered
        if removed_track is not None:
            disk_key = "Disk Drive" if "Disk Drive" in state["device_queues"] else "Disk"
            if disk_key in state["device_queues"]:
                queue = state["device_queues"][disk_key]
                if removed_track in queue:
                    queue.remove(removed_track)
        return len(state["io_queue"]) < before
    except Exception:
        return False


def clear_io_queue() -> None:
    try:
        state = init_system_state()
        state["io_queue"] = []
        state["last_result"] = None
        for device_name in list(state["device_queues"].keys()):
            state["device_queues"][device_name] = []
    except Exception:
        return


def is_device_connected(name: str) -> bool:
    try:
        state = init_system_state()
        return any(device.get("name") == name for device in state["connected_devices"])
    except Exception:
        return False
