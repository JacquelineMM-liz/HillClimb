"""Modo consola: paso a paso, ejecución completa y métricas."""
from __future__ import annotations

import argparse
import random

from .benchmark import Benchmark
from .climber import HillClimber
from .fitness import EuclideanFitness, ManhattanFitness
from .models import StepResult, format_number
from .restart import NoRestart, RandomRestart
from .scenarios import ScenarioCatalog
from .strategies import STRATEGIES


def print_step(step: StepResult) -> None:
    print(f"\n--- Iteración {step.iteration} | estado={step.position} "
          f"f={format_number(step.fitness)} | reinicios={step.restarts}")
    for n in step.neighbors:
        if not n.valid:
            print(f"  {n.direction.name:<9} {n.position}  {n.blocked_by}")
            continue
        tag = "ELEGIDO" if n is step.chosen else ("mejora" if n.improves else "no mejora")
        print(f"  {n.direction.name:<9} {n.position}  f={format_number(n.fitness):>6}  "
              f"Δf={format_number(n.delta, True):>6}  {tag}")
    print(f"  Decisión: {step.message}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="main.py cli", description=__doc__)
    ap.add_argument("modo", choices=["paso", "auto", "bench"])
    ap.add_argument("--caso", choices=[k for k, _ in ScenarioCatalog.items()], default="B")
    ap.add_argument("--variante", choices=list(STRATEGIES), default="steepest")
    ap.add_argument("--aptitud", choices=["manhattan", "euclidiana"], default="manhattan")
    ap.add_argument("--reinicios", action="store_true")
    args = ap.parse_args(argv)

    maze = ScenarioCatalog.create(args.caso)
    fitness = ManhattanFitness() if args.aptitud == "manhattan" else EuclideanFitness()
    strategy = STRATEGIES[args.variante]()
    if args.modo == "bench":
        bench = Benchmark(maze, fitness)
        for policy in (NoRestart(), RandomRestart()):
            r = bench.evaluate(strategy, policy)
            print(" | ".join(r.as_row()))
        return
    climber = HillClimber(maze, fitness, strategy, RandomRestart() if args.reinicios else NoRestart(),
                          random.Random())
    while not climber.finished:
        print_step(climber.step())
        if args.modo == "paso" and not climber.finished:
            input("  [Enter para continuar]")
