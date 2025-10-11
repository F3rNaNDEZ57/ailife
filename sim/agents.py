from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random

@dataclass
class AgentConfig:
    start_energy: float
    move_cost: float
    eat_energy: float
    speed: int
    vision: int
    behavior: str  # "random" or "greedy"

@dataclass
class Creature:
    x: int
    y: int
    energy: float

def init_agents(n: int, world, cfg: AgentConfig):
    agents: List[Creature] = []
    for _ in range(n):
        x = random.randrange(0, world.cfg.width)
        y = random.randrange(0, world.cfg.height)
        agents.append(Creature(x=x, y=y, energy=cfg.start_energy))
    return agents
