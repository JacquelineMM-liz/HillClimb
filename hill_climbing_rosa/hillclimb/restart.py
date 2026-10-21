"""Mecanismos de mitigación del estancamiento (patrón Strategy)."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod

from .maze import Maze
from .models import Position


class RestartPolicy(ABC):
    """Decide si se puede reiniciar y desde qué estado."""
    label: str = ""

    @abstractmethod
    def allows(self, restarts_done: int) -> bool:
        ...

    def new_state(self, maze: Maze, rng: random.Random) -> Position:
        return rng.choice(maze.free_cells())


class NoRestart(RestartPolicy):
    label = "sin reinicios"

    def allows(self, restarts_done: int) -> bool:
        return False


class RandomRestart(RestartPolicy):
    """Random-restart Hill Climbing: hasta `max_restarts` reinicios en celdas libres al azar."""

    def __init__(self, max_restarts: int = 20) -> None:
        self.max_restarts = max_restarts
        self.label = "con reinicios"

    def allows(self, restarts_done: int) -> bool:
        return restarts_done < self.max_restarts
