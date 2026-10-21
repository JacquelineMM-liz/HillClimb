"""Espacio de estados: una cuadrícula 2D con muros, inicio y meta."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Set

from .models import Position


class Maze:
    """Laberinto rectangular. Encapsula qué celdas son válidas; no sabe nada del algoritmo."""

    def __init__(self, width: int, height: int, start: Position, goal: Position,
                 walls: Iterable[Position] = ()) -> None:
        self._width, self._height = width, height
        self._start, self._goal = start, goal
        self._walls: Set[Position] = set(walls)
        if start in self._walls or goal in self._walls:
            raise ValueError("El inicio y la meta no pueden ser muros.")

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def start(self) -> Position:
        return self._start

    @property
    def goal(self) -> Position:
        return self._goal

    @property
    def walls(self) -> frozenset:
        return frozenset(self._walls)

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self._width and 0 <= pos.y < self._height

    def is_wall(self, pos: Position) -> bool:
        return pos in self._walls

    def is_free(self, pos: Position) -> bool:
        return self.in_bounds(pos) and not self.is_wall(pos)

    def blocked_reason(self, pos: Position) -> str:
        """Devuelve '' si la celda es transitable, o el motivo ('fuera' o 'muro')."""
        if not self.in_bounds(pos):
            return "fuera"
        return "muro" if self.is_wall(pos) else ""

    def toggle_wall(self, pos: Position) -> bool:
        """Pone o quita un muro. Devuelve False si la celda es el inicio, la meta o está fuera."""
        if pos in (self._start, self._goal) or not self.in_bounds(pos):
            return False
        self._walls.symmetric_difference_update({pos})
        return True

    def cells(self) -> Iterator[Position]:
        """Todas las celdas, recorridas por filas (orden estable para reproducibilidad)."""
        for y in range(self._height):
            for x in range(self._width):
                yield Position(x, y)

    def free_cells(self) -> List[Position]:
        return [p for p in self.cells() if not self.is_wall(p)]
