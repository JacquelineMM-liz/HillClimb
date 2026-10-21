"""Objetos de valor (inmutables) que comparten todas las capas del proyecto."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


@dataclass(frozen=True, order=True)
class Position:
    """Una celda (x, y) de la cuadrícula. Es un estado s del espacio de búsqueda S."""
    x: int
    y: int

    def shifted(self, direction: "Direction") -> "Position":
        return Position(self.x + direction.dx, self.y + direction.dy)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclass(frozen=True)
class Direction:
    """Un movimiento elemental del operador de vecindad N(s)."""
    name: str
    dx: int
    dy: int


# Orden fijo de evaluación de la vecindad: derecha, abajo, izquierda, arriba.
DIRECTIONS: Tuple[Direction, ...] = (
    Direction("Derecha", 1, 0),
    Direction("Abajo", 0, 1),
    Direction("Izquierda", -1, 0),
    Direction("Arriba", 0, -1),
)


class Status(Enum):
    """Resultado de una iteración del algoritmo."""
    MOVED = "Movimiento"
    GOAL_REACHED = "Meta alcanzada"
    LOCAL_MAXIMUM = "Máximo local"
    RESTARTED = "Reinicio aleatorio"
    MAX_ITERATIONS = "Límite de iteraciones"


def format_number(value: Optional[float], signed: bool = False) -> str:
    """Formatea f(s) o Δf de forma legible (enteros sin decimales, 2 decimales como máximo)."""
    if value is None:
        return "–"
    rounded = round(value, 2)
    if rounded == 0:
        rounded = 0.0
    return f"{rounded:+g}" if signed else f"{rounded:g}"


@dataclass(frozen=True)
class NeighborEval:
    """Evaluación de un vecino: su aptitud f(vecino) y la variación Δf respecto al estado actual."""
    direction: Direction
    position: Position
    valid: bool
    fitness: Optional[float] = None
    delta: Optional[float] = None
    blocked_by: str = ""  # "muro" o "fuera" cuando valid es False

    @property
    def improves(self) -> bool:
        return self.valid and self.delta is not None and self.delta > 0


@dataclass(frozen=True)
class StepResult:
    """Telemetría completa de una iteración."""
    iteration: int
    position: Position
    fitness: float
    neighbors: Tuple[NeighborEval, ...]
    chosen: Optional[NeighborEval]
    status: Status
    message: str
    new_position: Position
    restarts: int


@dataclass(frozen=True)
class RunResult:
    """Resumen de una ejecución completa."""
    success: bool
    iterations: int
    restarts: int
    final_position: Position
    final_fitness: float
    segments: Tuple[Tuple[Position, ...], ...]
    elapsed_ms: float
