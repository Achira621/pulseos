# OS I/O Device Scheduling Simulator - Agent Handoff Plan

## Project Overview
A modular Streamlit application simulating I/O device scheduling algorithms (FCFS, SSTF, SCAN) with a dark, analog, hacker-lab aesthetic.

## Architecture

```
os_miniproject/
├── app.py                 # Main Streamlit entry point
├── core/
│   ├── __init__.py
│   ├── schedulers.py      # Scheduling algorithm implementations
│   └── models.py          # Data models (IORequest, DiskDevice, etc.)
├── views/
│   ├── __init__.py
│   ├── dashboard.py       # Main dashboard view
│   ├── scheduler_view.py  # Algorithm comparison view
│   └── metrics_view.py    # System metrics and logs
├── utils/
│   ├── __init__.py
│   ├── metrics.py         # Fake system metrics generation
│   ├── logger.py          # System log simulation
│   └── styling.py         # CSS and theme utilities
├── animations/
│   ├── __init__.py
│   ├── lottie_loader.py   # Lottie animation loading
│   └── transitions.py     # fake flicker / delay transitions
├── assets/
│   └── animations/        # Lottie JSON files
└── requirements.txt
```

## Module Responsibilities

### core/schedulers.py
- **FCFSScheduler**: First-Come-First-Serve implementation
- **SSTFScheduler**: Shortest-Seek-Time-First implementation  
- **SCANScheduler**: SCAN/Elevator algorithm implementation
- Each returns execution timeline with seek times, head movement

### core/models.py
- **IORequest**: Represents a single I/O request (track, arrival_time, priority)
- **DiskDevice**: Simulates disk with head position, total_tracks
- **ScheduleResult**: Contains execution order, total_seek_time, head_movements

### utils/metrics.py
- Generates fake CPU usage, memory pressure, disk I/O stats
- Provides realistic-looking system telemetry
- Functions: `get_fake_cpu()`, `get_fake_memory()`, `get_disk_stats()`

### utils/logger.py
- Simulates system log entries with timestamps
- GeneratesINFO/WARNING/ERROR messages
- Functions: `generate_log_entry()`, `get_system_logs()`

### utils/styling.py
- Contains all CSS for dark hacker aesthetic
- Scanline overlay, CRT effects, muted color palette
- Functions: `get_dark_theme_css()`, `get_scanline_overlay()`

### views/dashboard.py
- Main landing page with queue visualization
- Controls for adding I/O requests
- Real-time simulation status

### views/scheduler_view.py
- Algorithm selector and comparison
- Plotly graphs for seek time visualization
- Side-by-side performance metrics

### views/metrics_view.py
- Fake system metrics dashboard
- Scrolling log viewer
- Device status indicators

### animations/lottie_loader.py / animations/transitions.py
- Loads local Lottie JSON safely
- Provides terminal-style fake transition helpers
- Functions: `render_lottie()`, `play_transition()`

## Key Design Decisions

1. **Fault Tolerance**: Every function wrapped in try-except with logging
2. **Simplicity Over Complexity**: Algorithms are simple textbook implementations
3. **Visual Complexity**: Advanced CSS overlays and Plotly graphs create "impressive" feel
4. **Fake Data**: Realistic-looking metrics without actual system access

## State Management
- Use Streamlit session_state for:
  - Current I/O queue
  - Selected algorithm
  - Simulation results
  - System metrics

## CSS Styling Convention
- Background: #0a0a0a to #1a1a1a (near black)
- Text: #00ff41 (muted green, not neon)
- Accents: #ff6b35 (amber), #4a9eff (cool blue)
- Scanlines: Semi-transparent horizontal lines
- CRT effect: Subtle vignette and screen curvature

## Algorithm Details

### FCFS (First-Come-First-Serve)
- Process requests in arrival order
- Simple but may cause starvation

### SSTF (Shortest-Seek-Time-First)
- Always pick request closest to current head
- More efficient than FCFS
- May cause starvation for distant requests

### SCAN (Elevator Algorithm)
- Head moves in one direction, servicing requests
- Reverses at end, continues servicing
- Better fairness than SSTF

## Performance Metrics Tracked
- Total Seek Time (sum of all head movements)
- Average Seek Time (total / request count)
- Number of Head Reversals
- Request Wait Time
- Throughput (requests/second)

## Dependencies
- streamlit >= 1.28.0
- plotly >= 5.18.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- streamlit-lottie >= 0.0.3

## Known Issues / TODOs
- [ ] Add more scheduling algorithms (LOOK, C-SCAN)
- [ ] Implement actual animation playback control
- [ ] Add request priority visualization
- [ ] Persist simulation state to disk

## Testing Approach
- Test each scheduler with known input sequences
- Verify seek time calculations match manual computation
- Check edge cases (empty queue, single request, same track requests)

## Color Palette (Muted Hacker Theme)
```
--bg-primary: #0a0a0a
--bg-secondary: #141414
--bg-tertiary: #1e1e1e
--text-primary: #00ff41 (matrix green, slightly dimmed)
--text-secondary: #7a7a7a
--accent-amber: #ff6b35
--accent-blue: #4a9eff
--accent-red: #ff4757
--border-color: #2a2a2a
--scanline-color: rgba(0, 255, 65, 0.03)
```

## Contact Points
- All views import from core/ and utils/
- app.py orchestrates view rendering
- Session state is primary communication channel
