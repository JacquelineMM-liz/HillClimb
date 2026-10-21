"""El algoritmo: un HillClimber compone laberinto, aptitud, estrategia y política de reinicio."""
from __future__ import annotations

import random
import time
from typing import List, Optional, Tuple

from .fitness import FitnessFunction
from .maze import Maze
from .models import (DIRECTIONS, NeighborEval, Position, RunResult, Status, StepResult,
                     format_number)
from .restart import NoRestart, RestartPolicy
from .strategies import SelectionStrategy


class HillClimber:
    """Ejecuta Hill Climbing iteración por iteración (`step`) o completo (`run`)."""

    def __init__(self, maze: Maze, fitness: FitnessFunction, strategy: SelectionStrategy,
                 restart_policy: Optional[RestartPolicy] = None,
                 rng: Optional[random.Random] = None, max_iterations: int = 400) -> None:
        self.maze = maze
        self.fitness = fitness
        self.strategy = strategy
        self.restart_policy = restart_policy or NoRestart()
        self.rng = rng or random.Random()
        self.max_iterations = max_iterations
        self.reset()

    # ---- estado observable -------------------------------------------------
    @property
    def current(self) -> Position:
        return self._current

    @property
    def current_fitness(self) -> float:
        return self.fitness(self._current, self.maze)

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def restarts(self) -> int:
        return self._restarts

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def success(self) -> bool:
        return self._success

    @property
    def last_result(self) -> Optional[StepResult]:
        return self._last

    @property
    def segments(self) -> Tuple[Tuple[Position, ...], ...]:
        """Trayectorias recorridas; cada reinicio abre un segmento nuevo."""
        return tuple(tuple(s) for s in self._segments)

    # ---- control ------------------------------------------------------------
    def reset(self, start: Optional[Position] = None) -> None:
        self._current = start or self.maze.start
        self._segments: List[List[Position]] = [[self._current]]
        self._iteration = 0
        self._restarts = 0
        self._finished = False
        self._success = False
        self._last: Optional[StepResult] = None

    def evaluate_neighbors(self, position: Position) -> Tuple[NeighborEval, ...]:
        """Genera N(s) y evalúa f(vecino) y Δf para cada vecino válido."""
        f_here = self.fitness(position, self.maze)
        evals = []
        for direction in DIRECTIONS:
            pos = position.shifted(direction)
            reason = self.maze.blocked_reason(pos)
            if reason:
                evals.append(NeighborEval(direction, pos, False, blocked_by=reason))
            else:
                f_n = self.fitness(pos, self.maze)
                evals.append(NeighborEval(direction, pos, True, f_n, f_n - f_here))
        return tuple(evals)

    def step(self) -> StepResult:
        """Avanza una iteración. Si ya terminó, devuelve la última telemetría."""
        if self._finished and self._last is not None:
            return self._last
        self._iteration += 1
        here = self._current
        f_here = self.fitness(here, self.maze)
        neighbors = self.evaluate_neighbors(here)
        chosen = self.strategy.choose(neighbors, self.rng)
        new_pos = here

        if chosen is not None:
            status = Status.MOVED
            new_pos = chosen.position
            message = (f"Se mueve a {chosen.direction.name.lower()} {new_pos}: "
                       f"Δf = {format_number(chosen.delta, signed=True)}.")
            self._current = new_pos
            self._segments[-1].append(new_pos)
        elif here == self.maze.goal:
            status = Status.GOAL_REACHED
            message = f"Óptimo global alcanzado: f = {format_number(f_here)}. Terminación exitosa."
            self._finished = self._success = True
        elif self.restart_policy.allows(self._restarts):
            self._restarts += 1
            new_pos = self.restart_policy.new_state(self.maze, self.rng)
            status = Status.RESTARTED
            message = (f"Máximo local en {here} (ningún vecino mejora). "
                       f"Reinicio aleatorio #{self._restarts} en {new_pos}.")
            self._current = new_pos
            self._segments.append([new_pos])
        else:
            status = Status.LOCAL_MAXIMUM
            message = (f"Atrapado en máximo local f = {format_number(f_here)}: ningún vecino "
                       f"tiene Δf > 0 y la meta no se alcanzó.")
            self._finished = True

        if not self._finished and self._iteration >= self.max_iterations:
            status, message, self._finished = (Status.MAX_ITERATIONS,
                                               f"Límite de {self.max_iterations} iteraciones.", True)

        self._last = StepResult(self._iteration, here, f_here, neighbors, chosen, status,
                                message, new_pos, self._restarts)
        return self._last

    def run(self) -> RunResult:
        """Ejecuta hasta terminar y devuelve el resumen."""
        t0 = time.perf_counter()
        while not self._finished:
            self.step()
        return RunResult(self._success, self._iteration, self._restarts, self._current,
                         self.current_fitness, self.segments,
                         (time.perf_counter() - t0) * 1000)
