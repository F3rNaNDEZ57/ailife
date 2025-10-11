from __future__ import annotations
import argparse
import os
import yaml
import numpy as np

from sim.world import GridWorld, WorldConfig
from sim.agents import init_agents, AgentConfig
from sim.engine import Engine, EngineConfig
from sim.utils import seed_everything, make_run_id, RunLogger

def load_cfg(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def main():
    ap = argparse.ArgumentParser(description="A‑Life Starter")
    ap.add_argument("--config", type=str, default="cfg/default.yaml", help="Path to YAML config")
    ap.add_argument("--headless", action="store_true", help="Run without a window")
    ap.add_argument("--steps", type=int, default=10000, help="Steps for headless mode")
    ap.add_argument("--seed", type=int, default=None, help="RNG seed (overrides config)")
    args = ap.parse_args()

    cfg = load_cfg(args.config)

    # Seeding
    seed_val = args.seed if args.seed is not None else cfg.get("seed")
    seed = seed_everything(seed_val)
    print(f"[seed] {seed}")

    # Paths
    ensure_dir("data")
    run_id = make_run_id()
    run_dir = os.path.join("data", run_id)
    ensure_dir(run_dir)

    # World
    wcfg = cfg["world"]
    world = GridWorld(
        WorldConfig(
            width=wcfg["width"],
            height=wcfg["height"],
            cell_size=wcfg["cell_size"],
            initial_food=wcfg["initial_food"],
            food_spawn_per_step=wcfg["food_spawn_per_step"],
            max_food=wcfg["max_food"],
        ),
        rng=np.random.default_rng(seed),
    )

    # Agents
    acfg_dict = cfg["agents"]
    acfg = AgentConfig(
        start_energy=acfg_dict["start_energy"],
        move_cost=acfg_dict["move_cost"],
        eat_energy=acfg_dict["eat_energy"],
        speed=acfg_dict["speed"],
        vision=acfg_dict["vision"],
        behavior=acfg_dict["behavior"],
    )
    agents = init_agents(cfg["agents"]["count"], world, acfg)

    # Engine
    ecfg_dict = cfg["engine"]
    ecfg = EngineConfig(
        dt=ecfg_dict["dt"],
        max_fps=ecfg_dict["max_fps"],
        log_every_steps=ecfg_dict["log_every_steps"],
        screenshot_every_steps=ecfg_dict.get("screenshot_every_steps", 0),
    )

    # Logger
    log_path = os.path.join(run_dir, "metrics.csv")
    logger = RunLogger(log_path, fieldnames=["step", "population", "mean_energy", "food"])

    engine = Engine(
        world=world,
        agents=agents,
        acfg=acfg,
        ecfg=ecfg,
        rng=np.random.default_rng(seed + 1),
        logger=logger,
        screenshots_path=run_dir,
    )

    try:
        if args.headless:
            engine.run_headless(args.steps)
            print(f"[done] Headless run complete. Logs at: {log_path}")
        else:
            engine.run_pygame()
    finally:
        logger.close()

if __name__ == "__main__":
    main()
