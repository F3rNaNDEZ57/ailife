from __future__ import annotations
import time
import pygame
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from .world import GridWorld, WorldConfig
from .agents import Creature, AgentConfig
from .systems import MovementSystem, IntakeSystem, EnergySystem, RenderSystem
from .utils import RunLogger

@dataclass
class EngineConfig:
    dt: float
    max_fps: int
    log_every_steps: int
    screenshot_every_steps: int = 0

class Engine:
    def __init__(
        self,
        world: GridWorld,
        agents: List[Creature],
        acfg: AgentConfig,
        ecfg: EngineConfig,
        rng: np.random.Generator,
        logger: Optional[RunLogger] = None,
        screenshots_path: Optional[str] = None,
    ):
        self.world = world
        self.agents = agents
        self.acfg = acfg
        self.ecfg = ecfg
        self.rng = rng
        self.logger = logger
        self.screenshots_path = screenshots_path
        # Systems
        self.move = MovementSystem(world, agents, acfg, rng)
        self.intake = IntakeSystem(world, agents, acfg)
        self.energy = EnergySystem(agents)
        self.render = RenderSystem(world, agents)
        # State
        self.step_count = 0
        self._last_log = 0

    def step(self):
        # One fixed simulation step
        self.move.step()
        self.intake.step()
        self.energy.step()
        self.world.step_regrow()
        self.step_count += 1

        # Logging
        if self.logger and (self.step_count - self._last_log) >= self.ecfg.log_every_steps:
            self._last_log = self.step_count
            self._log_row()

    def _log_row(self):
        pop = len(self.agents)
        mean_energy = sum(a.energy for a in self.agents)/pop if pop > 0 else 0.0
        row = {
            "step": self.step_count,
            "population": pop,
            "mean_energy": round(mean_energy, 3),
            "food": self.world.food_count,
        }
        self.logger.log(row)

    def run_headless(self, steps: int):
        for _ in range(steps):
            self.step()

    def run_pygame(self):
        pygame.init()
        clock = pygame.time.Clock()
        self.render.init_display()

        accumulator = 0.0
        last = time.perf_counter()
        running = True
        screenshot_id = 0

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Fixed-step simulation
            now = time.perf_counter()
            frame_time = now - last
            last = now
            accumulator += frame_time

            dt = self.ecfg.dt
            while accumulator >= dt:
                self.step()
                accumulator -= dt

            self.render.draw()

            # Optional screenshots
            if self.ecfg.screenshot_every_steps and self.step_count % self.ecfg.screenshot_every_steps == 0 and self.step_count > 0:
                path = f"{self.screenshots_path}/shot-{screenshot_id:05d}.png"
                pygame.image.save(self.render.surface, path)
                screenshot_id += 1

            clock.tick(self.ecfg.max_fps)

        pygame.quit()
