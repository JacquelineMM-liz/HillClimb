"""Escenarios de prueba obligatorios: A (éxito) y B (trampa cóncava)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from .maze import Maze
from .models import Position as P

W, H = 15, 11


def _case_a() -> Maze:
    walls = [P(*t) for t in [(4, 3), (5, 6), (8, 2), (9, 5), (10, 8), (6, 8), (3, 7), (11, 3)]]
    return Maze(W, H, P(1, 1), P(13, 9), walls)


def _case_b() -> Maze:
    walls = [P(7, y) for y in range(2, 9)] + [P(x, 2) for x in (4, 5, 6)] + [P(x, 8) for x in (4, 5, 6)]
    return Maze(W, H, P(5, 5), P(12, 5), walls)


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    builder: Callable[[], Maze]


class ScenarioCatalog:
    """Fábrica de laberintos: cada llamada a `create` devuelve una copia nueva y editable."""
    _SCENARIOS: Dict[str, Scenario] = {
        "A": Scenario("A", "Caso A: camino despejado", _case_a),
        "B": Scenario("B", "Caso B: trampa cóncava", _case_b),
    }

    @classmethod
    def create(cls, key: str) -> Maze:
        return cls._SCENARIOS[key].builder()

    @classmethod
    def items(cls) -> List[Tuple[str, str]]:
        return [(s.key, s.title) for s in cls._SCENARIOS.values()]
