from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import pygame
import numpy as np

from .world import GridWorld, FOOD, EMPTY
from .agents import Creature, AgentConfig

Vec2i = Tuple[int, int]

DIRS: List[Vec2i] = [(1,0),(-1,0),(0,1),(0,-1)]

@dataclass
class SystemsConfig:
    pass

class MovementSystem:
    def __init__(self, world: GridWorld, agents: List[Creature], cfg: AgentConfig, rng: np.random.Generator):
        self.world = world
        self.agents = agents
        self.cfg = cfg
        self.rng = rng

    def nearest_food_dir(self, x: int, y: int, vision: int) -> Optional[Vec2i]:
        # Manhattan search within vision radius; return step direction toward nearest food
        best = None
        best_dist = 99999
        h, w = self.world.cfg.height, self.world.cfg.width
        for dy in range(-vision, vision+1):
            for dx in range(-vision, vision+1):
                if abs(dx) + abs(dy) > vision:
                    continue
                nx = (x + dx) % w
                ny = (y + dy) % h
                if self.world.grid[ny, nx] == FOOD:
                    dist = abs(dx) + abs(dy)
                    if 0 < dist < best_dist:
                        best_dist = dist
                        # Step one cell toward the food
                        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
                        best = (step_x, step_y)
        return best

    def step(self):
        for a in list(self.agents):
            # Decide direction
            if self.cfg.behavior == "greedy":
                d = self.nearest_food_dir(a.x, a.y, self.cfg.vision)
                if d is None:
                    d = random.choice(DIRS)
            else:
                d = random.choice(DIRS)
            # Move speed steps (usually 1)
            for _ in range(self.cfg.speed):
                nx, ny = self.world.wrap(a.x + d[0], a.y + d[1])
                a.x, a.y = nx, ny
                a.energy -= self.cfg.move_cost

class IntakeSystem:
    def __init__(self, world: GridWorld, agents: List[Creature], cfg: AgentConfig):
        self.world = world
        self.agents = agents
        self.cfg = cfg

    def step(self):
        for a in self.agents:
            if self.world.grid[a.y, a.x] == FOOD:
                a.energy += self.cfg.eat_energy
                self.world.grid[a.y, a.x] = EMPTY

class EnergySystem:
    def __init__(self, agents: List[Creature]):
        self.agents = agents

    def step(self):
        # Remove dead agents
        alive = [a for a in self.agents if a.energy > 0]
        self.agents.clear()
        self.agents.extend(alive)

class RenderSystem:
    def __init__(self, world: GridWorld, agents: List[Creature]):
        self.world = world
        self.agents = agents
        self.surface = None

    def init_display(self):
        w = self.world.cfg.width * self.world.cfg.cell_size
        h = self.world.cfg.height * self.world.cfg.cell_size
        self.surface = pygame.display.set_mode((w, h))
        pygame.display.set_caption("A‑Life Starter")

    def draw(self):
        cs = self.world.cfg.cell_size
        surf = self.surface
        surf.fill((20, 20, 24))

        # Draw food
        food_y, food_x = (self.world.grid == FOOD).nonzero()
        for y, x in zip(food_y, food_x):
            rect = pygame.Rect(x*cs, y*cs, cs, cs)
            pygame.draw.rect(surf, (0, 180, 0), rect)

        # Draw agents
        for a in self.agents:
            cx = a.x*cs + cs//2
            cy = a.y*cs + cs//2
            r = max(2, cs//2 - 1)
            pygame.draw.circle(surf, (60, 140, 255), (cx, cy), r)

        pygame.display.flip()
