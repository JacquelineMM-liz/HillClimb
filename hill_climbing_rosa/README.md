# ♥ Hill Climbing rosa: laberinto con trampas

Demostración en **Python 3.9+** (solo biblioteca estándar) del algoritmo Hill Climbing, con interfaz gráfica rosa (tkinter), modo consola y pruebas unitarias.

## Cómo ejecutarlo
```
python main.py                                  # interfaz gráfica rosa
python main.py cli auto  --caso B --reinicios   # consola, ejecución completa
python main.py cli paso  --caso B               # consola, paso a paso (Enter avanza)
python main.py cli bench --caso B --variante first
python -m unittest discover -s tests -v         # pruebas
```
Si la interfaz no abre, instala tkinter (en Linux: `sudo apt install python3-tk`) o usa el modo consola.

## Qué incluye (requisitos de la práctica)
| Requisito | Dónde |
|---|---|
| Paso a paso | botón **Paso** / `cli paso` |
| Telemetría (estado, f, vecinos con f y Δf, razón de decisión) | panel «Telemetría» / `cli` |
| Caso A: éxito | escenario «Caso A» |
| Caso B: máximo local | escenario «Caso B» |
| Mitigación | casilla **Reinicios aleatorios** (`RandomRestart`) |
| Métricas (éxito, estancamiento, iteraciones, tiempo) | botón **Ejecutar métricas** / `cli bench` |

## Arquitectura orientada a objetos
```
hillclimb/
  models.py      Position, Direction, NeighborEval, StepResult, RunResult, Status   (objetos de valor inmutables)
  maze.py        Maze                      espacio de estados: muros, inicio, meta
  fitness.py     FitnessFunction (ABC) ─┬─ ManhattanFitness
                                        └─ EuclideanFitness
  strategies.py  SelectionStrategy (ABC) ─┬─ SteepestAscent
                                          ├─ FirstChoice
                                          └─ Stochastic
  restart.py     RestartPolicy (ABC) ─┬─ NoRestart
                                      └─ RandomRestart
  climber.py     HillClimber           compone todo lo anterior; step() y run()
  benchmark.py   Benchmark, BenchmarkResult
  scenarios.py   ScenarioCatalog        fábrica de los casos A y B
  gui.py         PinkTheme, MazeCanvas, TelemetryPanel, MetricsPanel, App
  cli.py         modo consola
tests/           pruebas unitarias (unittest)
```
**Principios aplicados:** abstracción (clases base abstractas), polimorfismo y patrón *Strategy* (variantes y reinicios intercambiables sin tocar `HillClimber`), composición (el climber *tiene* un laberinto, una aptitud, una estrategia y una política), encapsulación (`Maze` oculta sus muros; `HillClimber` expone propiedades de solo lectura) y separación de responsabilidades (el núcleo no conoce la interfaz).

## Modelo del problema
- Estado: celda `(x, y)` libre. Vecindad: derecha, abajo, izquierda, arriba.
- Aptitud: `f(s) = −distancia a la meta` (Manhattan o euclidiana); se maximiza, óptimo `f = 0`.
- Un movimiento se acepta solo si `Δf > 0`.
- Caso B: trampa en forma de copa; desde `(6, 5)` ningún vecino mejora (`f = −6`).

## Añadir una variante
Crea una subclase de `SelectionStrategy` con `key`, `label` y `choose()`, y regístrala en `STRATEGIES`; aparecerá sola en la interfaz.
