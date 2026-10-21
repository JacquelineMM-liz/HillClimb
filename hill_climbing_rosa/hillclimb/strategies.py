"""Variantes de Hill Climbing como estrategias intercambiables de selección de vecino."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, Sequence, Type

from .models import NeighborEval


class SelectionStrategy(ABC):
    """Dada la vecindad evaluada, elige el siguiente vecino o None si ninguno mejora."""
    key: str = ""
    label: str = ""

    @abstractmethod
    def choose(self, neighbors: Sequence[NeighborEval], rng: random.Random) -> Optional[NeighborEval]:
        ...

    @staticmethod
    def _improving(neighbors: Sequence[NeighborEval]):
        return [n for n in neighbors if n.improves]


class SteepestAscent(SelectionStrategy):
    """Ascenso más pronunciado: el vecino con mayor Δf (en empate, el primero evaluado)."""
    key, label = "steepest", "Steepest-ascent"

    def choose(self, neighbors, rng):
        improving = self._improving(neighbors)
        return max(improving, key=lambda n: n.delta) if improving else None


class FirstChoice(SelectionStrategy):
    """Primer vecino que mejora, recorriendo la vecindad en orden aleatorio."""
    key, label = "first", "First-choice"

    def choose(self, neighbors, rng):
        if not self._improving(neighbors):
            return None
        order = list(neighbors)
        rng.shuffle(order)
        return next(n for n in order if n.improves)


class Stochastic(SelectionStrategy):
    """Elige al azar entre los que mejoran, con probabilidad proporcional a Δf."""
    key, label = "stoch", "Stochastic"

    def choose(self, neighbors, rng):
        improving = self._improving(neighbors)
        if not improving:
            return None
        return rng.choices(improving, weights=[n.delta for n in improving])[0]


STRATEGIES: Dict[str, Type[SelectionStrategy]] = {
    cls.key: cls for cls in (SteepestAscent, FirstChoice, Stochastic)
}
