---
trigger: always_on
---

def safe_execute(func, *args):
    try:
        return func(*args)
    except Exception as e:
        return {"error": str(e)}
🔹 Fallback Rules
Empty queue → return empty result
Invalid input → ignore safely
Graph fail → show text fallback
Missing data → use defaults