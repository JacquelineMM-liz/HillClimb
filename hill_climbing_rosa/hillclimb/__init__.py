"""Hill Climbing en un laberinto con trampas: paquete con diseño orientado a objetos."""
from .benchmark import Benchmark, BenchmarkResult
from .climber import HillClimber
from .fitness import EuclideanFitness, FitnessFunction, ManhattanFitness
from .maze import Maze
from .models import Direction, NeighborEval, Position, RunResult, Status, StepResult
from .restart import NoRestart, RandomRestart, RestartPolicy
from .scenarios import ScenarioCatalog
from .strategies import FirstChoice, SelectionStrategy, SteepestAscent, Stochastic, STRATEGIES

__all__ = [
    "Benchmark", "BenchmarkResult", "HillClimber", "EuclideanFitness", "FitnessFunction",
    "ManhattanFitness", "Maze", "Direction", "NeighborEval", "Position", "RunResult", "Status",
    "StepResult", "NoRestart", "RandomRestart", "RestartPolicy", "ScenarioCatalog", "FirstChoice",
    "SelectionStrategy", "SteepestAscent", "Stochastic", "STRATEGIES",
]
