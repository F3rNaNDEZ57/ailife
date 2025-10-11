from __future__ import annotations
import numpy as np
from dataclasses import dataclass

EMPTY = 0
FOOD = 1

@dataclass
class WorldConfig:
    width: int
    height: int
    cell_size: int
    initial_food: int
    food_spawn_per_step: int
    max_food: int

class GridWorld:
    def __init__(self, cfg: WorldConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        self.grid = np.zeros((cfg.height, cfg.width), dtype=np.uint8)
        self.spawn_food(cfg.initial_food)

    @property
    def food_count(self) -> int:
        return int((self.grid == FOOD).sum())

    def wrap(self, x: int, y: int):
        return x % self.cfg.width, y % self.cfg.height

    def spawn_food(self, amount: int):
        h, w = self.cfg.height, self.cfg.width
        empties = np.argwhere(self.grid == EMPTY)
        if len(empties) == 0:
            return
        amount = min(amount, len(empties), self.cfg.max_food - self.food_count)
        if amount <= 0:
            return
        idx = self.rng.choice(len(empties), size=amount, replace=False)
        points = empties[idx]
        self.grid[points[:,0], points[:,1]] = FOOD

    def step_regrow(self):
        # Try a fixed number of spawn attempts each step
        if self.food_count < self.cfg.max_food:
            self.spawn_food(self.cfg.food_spawn_per_step)
