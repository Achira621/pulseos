---
trigger: always_on
---

THEME
Dark, grainy, analog
No neon colors ❌
No modern glossy UI ❌
🎨 COLOR PALETTE
Background → #0d0d0d  
Panels → #1a1a1a  
Text → #d6d6d6  
Accent → muted green (#6b8f71)
📺 SCREEN EFFECT (MANDATORY)

Agent MUST implement:

Scanlines overlay
Slight blur
Noise/grain
Flicker transitions
🧾 FONT
Monospace only:
Courier New
JetBrains Mono (if available)
🧩 UI STYLE
Terminal-like commands
Debug panels
System logs instead of buttons

Example:

> INITIALIZE DEVICE
> RUN SCHEDULER
> VIEW METRICS
🎬 7. TRANSITION / ZOOM CONSTRAINTS
❗ DO NOT implement real zoom

Instead simulate using:

Lottie animations
Delays (time.sleep)
Text transitions
🔹 Required Transition Pattern
User action

Show log:

[CONNECTING...]
[SIGNAL UNSTABLE]
Short delay
Load next screen
🎥 Libraries MUST be used:
streamlit-lottie
time
Pillow (optional zoom crop)
