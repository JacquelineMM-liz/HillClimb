"""Métricas: tasa de éxito, estancamiento, iteraciones y tiempo sobre muchas ejecuciones."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Tuple

from .climber import HillClimber
from .fitness import FitnessFunction
from .maze import Maze
from .restart import RestartPolicy
from .strategies import SelectionStrategy


@dataclass(frozen=True)
class BenchmarkResult:
    label: str
    runs: int
    success_rate: float
    stuck_rate: float
    mean_iterations: float
    elapsed_ms: float

    def as_row(self) -> Tuple[str, ...]:
        return (self.label, f"{self.success_rate:.1f} %", f"{self.stuck_rate:.1f} %",
                f"{self.mean_iterations:.1f}", f"{self.elapsed_ms:.1f} ms")


class Benchmark:
    """Lanza `runs` ejecuciones desde celdas libres aleatorias (semilla fija = reproducible)."""

    def __init__(self, maze: Maze, fitness: FitnessFunction, runs: int = 500, seed: int = 1,
                 max_iterations: int = 400) -> None:
        self.maze, self.fitness = maze, fitness
        self.runs, self.seed, self.max_iterations = runs, seed, max_iterations

    def evaluate(self, strategy: SelectionStrategy, policy: RestartPolicy) -> BenchmarkResult:
        rng = random.Random(self.seed)
        cells = self.maze.free_cells()
        climber = HillClimber(self.maze, self.fitness, strategy, policy, rng, self.max_iterations)
        ok = total = 0
        t0 = time.perf_counter()
        for _ in range(self.runs):
            climber.reset(rng.choice(cells))
            result = climber.run()
            ok += result.success
            total += result.iterations
        elapsed = (time.perf_counter() - t0) * 1000
        label = f"{strategy.label} · {policy.label}"
        return BenchmarkResult(label, self.runs, 100 * ok / self.runs,
                               100 * (self.runs - ok) / self.runs, total / self.runs, elapsed)
