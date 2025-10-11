# A‑Life Starter (Pygame + Fixed-Step Engine)

A minimal artificial life sandbox with:
- Fixed‑step simulation (deterministic physics independent of FPS)
- Toroidal grid world with food spawning
- Agents with energy economy (move cost, eat to gain)
- Headless mode for fast experiments + CSV logging
- Configurable behavior (random vs. greedy toward food)

## Quickstart

```bash
# 1) Create a virtual env (recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run with a window
python main.py --config cfg/default.yaml

# 4) Headless run (no window), 10k steps, fixed seed
python main.py --config cfg/default.yaml --headless --steps 10000 --seed 42
```

Outputs (CSV logs, screenshots) go in `data/`.

## Structure
```
alife-starter/
  main.py
  sim/
    engine.py
    world.py
    agents.py
    systems.py
    utils.py
  cfg/
    default.yaml
  data/
  experiments/
  requirements.txt
  README.md
```
