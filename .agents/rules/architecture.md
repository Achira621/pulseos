---
trigger: always_on
---

MUST follow strict modular structure
Each module has single responsibility
No file > 200 lines
No circular imports
All modules must be reusable
📁 REQUIRED STRUCTURE
project/
│
├── app.py                      # entry point and routing
├── config.py                   # colors, constants, settings
│
├── views/                      # UI layers
│   ├── room_view.py
│   ├── device_view.py
│   ├── os_dashboard.py
│   ├── scheduler_view.py
│
├── core/                       # logic only
│   ├── scheduler.py           # FCFS, SSTF, SCAN
│   ├── queue_manager.py
│   ├── metrics.py             # performance calculation
│
├── animations/
│   ├── transitions.py         # fake zoom/flicker
│   ├── lottie_loader.py       # animation handling
│
├── utils/
SEPARATION OF CONCERNS (STRICT)
UI files → ONLY display logic
Core files → ONLY algorithms
Utils → helpers only

❌ UI must NOT calculate scheduling
❌ Core must NOT import Streamlit

🛡️ 4. FAULT TOLERANCE RULES

Every function MUST:

Use try-except
Return safe fallback values
Never crash UI