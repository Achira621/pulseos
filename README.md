# OS I/O Device Scheduling Simulator

A modular, fault-tolerant Python application using Streamlit that simulates I/O device scheduling algorithms in an operating system.

## Features

- **Three Scheduling Algorithms**: FCFS, SSTF, and SCAN
- **I/O Queue Management**: Add, view, and clear pending requests
- **Performance Comparison**: Side-by-side algorithm metrics
- **Real-time Visualization**: Disk head movement and request tracking
- **Fake System Metrics**: CPU, memory, disk I/O monitoring
- **System Log Simulation**: Realistic log entries with timestamps
- **Dark Hacker Aesthetic**: CRT scanlines, muted colors, terminal feel

## Project Structure

```
os_miniproject/
├── app.py                 # Main Streamlit entry point
├── core/
│   ├── __init__.py
│   ├── models.py          # Data models (IORequest, DiskDevice, etc.)
│   └── schedulers.py      # Scheduling algorithm implementations
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
│   └── transitions.py    # fake flicker / delay transitions
├── assets/
│   └── animations/        # Lottie JSON files
├── requirements.txt
├── PLAN_SHEET.md          # Agent handoff documentation
└── README.md
```

## Installation

1. Clone or navigate to the project directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## How to Use

### Dashboard
1. Add I/O requests using the sliders (track position, priority, burst time)
2. Click "ADD REQUEST" or "RANDOM" to add to queue
3. Select an algorithm (FCFS, SSTF, or SCAN)
4. Click "RUN SIMULATION" to execute

### Algorithm Comparison
1. Navigate to the comparison view
2. Click "RUN COMPARISON" to execute all algorithms
3. View side-by-side performance metrics

### System Metrics
1. View simulated CPU, memory, and disk I/O stats
2. Monitor process list
3. View system logs with severity filtering

## Algorithms

### FCFS (First-Come-First-Serve)
- Processes requests in arrival order
- Simple but may have high seek times
- No starvation

### SSTF (Shortest-Seek-Time-First)
- Always selects the request closest to current head
- Lower average seek time than FCFS
- May cause starvation for distant requests

### SCAN (Elevator Algorithm)
- Head moves in one direction, reverses at end
- Good balance of performance and fairness
- Prevents starvation

## Architecture

### Fault Tolerance
- All functions wrapped in try-except blocks
- Invalid inputs handled gracefully with defaults
- Partial results returned when possible

### Modularity
- Clear separation between core logic and views
- Reusable utility modules
- Data models independent of UI

## Customization

### Styling
Edit `utils/styling.py` to modify:
- Color palette
- CRT effects
- Component styles

### Algorithms
Edit `core/schedulers.py` to modify:
- Scheduling logic
- Metrics calculation
- Add new algorithms

## Dependencies

- streamlit >= 1.28.0
- plotly >= 5.18.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- streamlit-lottie >= 0.0.3

## License

MIT License
