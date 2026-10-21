"""Funciones de aptitud f(s). Se maximizan: la meta es la cima (f = 0)."""
from __future__ import annotations

import math
from abc import ABC, abstractmethod

from .maze import Maze
from .models import Position


class FitnessFunction(ABC):
    """Contrato: cuanto mayor es f(s), mejor es el estado."""
    label: str = ""

    @abstractmethod
    def __call__(self, position: Position, maze: Maze) -> float:
        ...


class ManhattanFitness(FitnessFunction):
    """f(s) = -(|x - gx| + |y - gy|)."""
    label = "Distancia Manhattan"

    def __call__(self, position: Position, maze: Maze) -> float:
        g = maze.goal
        return -float(abs(position.x - g.x) + abs(position.y - g.y))


class EuclideanFitness(FitnessFunction):
    """f(s) = -sqrt((x - gx)^2 + (y - gy)^2)."""
    label = "Distancia euclidiana"

    def __call__(self, position: Position, maze: Maze) -> float:
        g = maze.goal
        return -math.hypot(position.x - g.x, position.y - g.y)
