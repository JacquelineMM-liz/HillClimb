"""Interfaz gráfica (tkinter, sin dependencias externas) con tema rosa.

Clases: PinkTheme (estilos) · MazeCanvas (mapa) · TelemetryPanel · MetricsPanel · App (orquesta).
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Sequence, Tuple

from .benchmark import Benchmark, BenchmarkResult
from .climber import HillClimber
from .fitness import EuclideanFitness, FitnessFunction, ManhattanFitness
from .maze import Maze
from .models import Position, Status, StepResult, format_number
from .restart import NoRestart, RandomRestart
from .scenarios import ScenarioCatalog
from .strategies import STRATEGIES


class PinkTheme:
    """Paleta y estilos ttk. Un solo lugar para cambiar la estética."""
    BG, PANEL, CARD, GRID = "#fff0f6", "#ffe3ee", "#ffffff", "#ffd0e3"
    ACCENT, ACCENT_DARK, TEXT, MUTED = "#e64980", "#a61e4d", "#4a1830", "#9c6b84"
    WALL, OK, BAD, TRAIL_OLD = "#5c2a49", "#2b9a6b", "#c2255c", "#f783ac"
    LOW, HIGH = (255, 245, 249), (214, 51, 108)
    FONT = "Helvetica"

    @classmethod
    def blend(cls, t: float) -> str:
        """Color de la altitud: 0 = rosa muy claro, 1 = rosa intenso."""
        r, g, b = (round(lo + (hi - lo) * t) for lo, hi in zip(cls.LOW, cls.HIGH))
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def apply(cls, root: tk.Tk) -> None:
        root.configure(bg=cls.BG)
        s = ttk.Style(root)
        s.theme_use("clam")
        s.configure(".", background=cls.BG, foreground=cls.TEXT, font=(cls.FONT, 10))
        s.configure("Title.TLabel", font=(cls.FONT, 20, "bold"), foreground=cls.ACCENT_DARK)
        s.configure("Sub.TLabel", foreground=cls.MUTED)
        s.configure("Card.TLabel", background=cls.CARD)
        s.configure("CardTitle.TLabel", background=cls.CARD, foreground=cls.ACCENT_DARK,
                    font=(cls.FONT, 12, "bold"))
        s.configure("Bold.TLabel", background=cls.CARD, font=(cls.FONT, 10, "bold"))
        s.configure("Pink.TButton", background=cls.ACCENT, foreground="white", borderwidth=0,
                    padding=(14, 6), font=(cls.FONT, 10, "bold"))
        s.map("Pink.TButton", background=[("active", cls.ACCENT_DARK), ("pressed", cls.ACCENT_DARK)])
        s.configure("Soft.TButton", background=cls.PANEL, foreground=cls.ACCENT_DARK, borderwidth=0,
                    padding=(12, 6), font=(cls.FONT, 10, "bold"))
        s.map("Soft.TButton", background=[("active", cls.GRID)])
        s.configure("TCombobox", fieldbackground="white", background=cls.PANEL,
                    arrowcolor=cls.ACCENT_DARK, bordercolor=cls.GRID)
        s.configure("TCheckbutton", background=cls.BG)
        s.map("TCheckbutton", background=[("active", cls.BG)])
        s.configure("Treeview", background="white", fieldbackground="white", rowheight=24,
                    bordercolor=cls.GRID, foreground=cls.TEXT)
        s.configure("Treeview.Heading", background=cls.PANEL, foreground=cls.ACCENT_DARK,
                    font=(cls.FONT, 9, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", cls.GRID)], foreground=[("selected", cls.TEXT)])
        s.configure("Horizontal.TScale", background=cls.BG)


def card(parent: tk.Misc, **kw) -> tk.Frame:
    return tk.Frame(parent, bg=PinkTheme.CARD, highlightbackground=PinkTheme.GRID,
                    highlightthickness=1, **kw)


class MazeCanvas(tk.Canvas):
    """Dibuja el laberinto como mapa de altitud f(s), la trayectoria y los marcadores."""
    CELL = 40

    def __init__(self, parent: tk.Misc, on_cell_click: Callable[[Position], None]) -> None:
        super().__init__(parent, bg=PinkTheme.CARD, highlightthickness=0)
        self._on_cell_click = on_cell_click
        self.bind("<Button-1>", self._clicked)

    def _clicked(self, event: tk.Event) -> None:
        self._on_cell_click(Position(event.x // self.CELL, event.y // self.CELL))

    def draw(self, maze: Maze, fitness: FitnessFunction, climber: HillClimber) -> None:
        T, c = PinkTheme, self.CELL
        self.delete("all")
        self.config(width=maze.width * c, height=maze.height * c)
        values = {p: fitness(p, maze) for p in maze.cells()}
        lo, hi = min(values.values()), max(values.values())
        span = (hi - lo) or 1.0
        for p, v in values.items():
            x0, y0 = p.x * c, p.y * c
            if maze.is_wall(p):
                self.create_rectangle(x0, y0, x0 + c, y0 + c, fill=T.WALL, outline=T.WALL)
                continue
            t = (v - lo) / span
            self.create_rectangle(x0, y0, x0 + c, y0 + c, fill=T.blend(t), outline=T.GRID)
            self.create_text(x0 + c / 2, y0 + c / 2, text=format_number(v), font=(T.FONT, 7),
                             fill="#ffffff" if t > 0.55 else "#b5648a")
        last = len(climber.segments) - 1
        for i, seg in enumerate(climber.segments):
            if len(seg) > 1:
                pts = [coord for p in seg for coord in (p.x * c + c / 2, p.y * c + c / 2)]
                self.create_line(*pts, width=3, capstyle="round", joinstyle="round",
                                 fill=T.ACCENT_DARK if i == last else T.TRAIL_OLD,
                                 dash=() if i == last else (4, 3))
        s = maze.start
        self.create_rectangle(s.x * c + 11, s.y * c + 11, s.x * c + c - 11, s.y * c + c - 11,
                              fill=T.TEXT, outline="white", width=2)
        g = maze.goal
        self.create_oval(g.x * c + 4, g.y * c + 4, g.x * c + c - 4, g.y * c + c - 4,
                         fill="white", outline=T.OK, width=3)
        self.create_text(g.x * c + c / 2, g.y * c + c / 2 + 1, text="♥", fill=T.ACCENT,
                         font=(T.FONT, 18, "bold"))
        cur = climber.current
        stuck = climber.finished and not climber.success
        self.create_oval(cur.x * c + 11, cur.y * c + 11, cur.x * c + c - 11, cur.y * c + c - 11,
                         fill=T.BAD if stuck else T.ACCENT_DARK, outline="white", width=2)


class TelemetryPanel(tk.Frame):
    """Estado actual, f(actual), vecinos evaluados (f y Δf) y razón de la decisión."""

    def __init__(self, parent: tk.Misc) -> None:
        T = PinkTheme
        super().__init__(parent, bg=T.CARD, highlightbackground=T.GRID, highlightthickness=1,
                         padx=12, pady=10)
        ttk.Label(self, text="Telemetría", style="CardTitle.TLabel").grid(row=0, column=0,
                                                                         columnspan=4, sticky="w")
        self._vars = {k: tk.StringVar(value="–") for k in ("Iteración", "Estado", "f(actual)", "Reinicios")}
        for i, (name, var) in enumerate(self._vars.items()):
            r, col = 1 + i // 2, (i % 2) * 2
            ttk.Label(self, text=name, style="Card.TLabel", foreground=T.MUTED).grid(
                row=r, column=col, sticky="w", padx=(0, 8))
            ttk.Label(self, textvariable=var, style="Bold.TLabel").grid(
                row=r, column=col + 1, sticky="w", padx=(0, 18))
        cols = ("vecino", "celda", "f", "df", "nota")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=4)
        for col, title, w in zip(cols, ("Vecino", "Celda", "f(vecino)", "Δf", "Nota"),
                                 (80, 70, 70, 50, 90)):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor="w")
        self.tree.tag_configure("pick", background=T.GRID)
        self.tree.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 8))
        self.reason = tk.Label(self, text="Pulsa «Paso» para comenzar.", wraplength=360,
                               justify="left", anchor="w", bg=T.PANEL, fg=T.TEXT, padx=10, pady=8,
                               font=(T.FONT, 10))
        self.reason.grid(row=4, column=0, columnspan=4, sticky="ew")

    def show(self, step: Optional[StepResult], climber: HillClimber) -> None:
        T = PinkTheme
        self._vars["Iteración"].set(str(climber.iteration))
        self._vars["Estado"].set(str(climber.current))
        self._vars["f(actual)"].set(format_number(climber.current_fitness))
        self._vars["Reinicios"].set(str(climber.restarts))
        self.tree.delete(*self.tree.get_children())
        if step is None:
            self.reason.config(text="Pulsa «Paso» para comenzar.", fg=T.TEXT)
            return
        for n in step.neighbors:
            if not n.valid:
                row = (n.direction.name, "–", "–", "–", n.blocked_by)
            else:
                note = "elegido" if n is step.chosen else ("mejora" if n.improves else "no mejora")
                row = (n.direction.name, str(n.position), format_number(n.fitness),
                       format_number(n.delta, True), note)
            self.tree.insert("", "end", values=row, tags=("pick",) if n is step.chosen else ())
        color = {Status.GOAL_REACHED: T.OK, Status.LOCAL_MAXIMUM: T.BAD}.get(step.status, T.TEXT)
        self.reason.config(text=step.message, fg=color)


class MetricsPanel(tk.Frame):
    """Tabla de métricas comparando con y sin reinicios."""

    def __init__(self, parent: tk.Misc) -> None:
        T = PinkTheme
        super().__init__(parent, bg=T.CARD, highlightbackground=T.GRID, highlightthickness=1,
                         padx=12, pady=10)
        ttk.Label(self, text="Métricas (500 ejecuciones desde celdas libres aleatorias)",
                  style="CardTitle.TLabel").pack(anchor="w")
        cols = ("cfg", "ok", "stuck", "it", "ms")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=2)
        for col, title, w in zip(cols, ("Configuración", "Éxito", "Estancado", "Iteraciones (media)",
                                        "Tiempo"), (300, 80, 90, 140, 100)):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="x", pady=(8, 0))

    def set_results(self, results: Sequence[BenchmarkResult]) -> None:
        self.tree.delete(*self.tree.get_children())
        for r in results:
            self.tree.insert("", "end", values=r.as_row())


class App(tk.Tk):
    """Ventana principal: conecta los controles con el modelo (maze, fitness, climber)."""

    def __init__(self) -> None:
        super().__init__()
        self.title("♥ Hill Climbing · laberinto con trampas")
        PinkTheme.apply(self)
        self.resizable(False, False)
        self._fitness_options = {ManhattanFitness.label: ManhattanFitness,
                                 EuclideanFitness.label: EuclideanFitness}
        self._strategy_options = {cls.label: cls for cls in STRATEGIES.values()}
        self._scenario_options = {title: key for key, title in ScenarioCatalog.items()}
        self._auto_job: Optional[str] = None
        self._build_widgets()
        self._load_scenario()

    # ---- construcción de la interfaz ---------------------------------------
    def _build_widgets(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=16, pady=(14, 6))
        ttk.Label(header, text="♥ Hill Climbing", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="f(s) = −distancia a la meta · Clic en el mapa para poner o quitar muros",
                  style="Sub.TLabel").pack(anchor="w")

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=16, pady=6)
        self.scenario_var = tk.StringVar(value=ScenarioCatalog.items()[0][1])
        self.strategy_var = tk.StringVar(value=next(iter(self._strategy_options)))
        self.fitness_var = tk.StringVar(value=ManhattanFitness.label)
        self.restart_var = tk.BooleanVar(value=False)
        for var, values, width in ((self.scenario_var, list(self._scenario_options), 24),
                                   (self.strategy_var, list(self._strategy_options), 16),
                                   (self.fitness_var, list(self._fitness_options), 20)):
            box = ttk.Combobox(bar, textvariable=var, values=values, state="readonly", width=width)
            box.pack(side="left", padx=(0, 8))
            box.bind("<<ComboboxSelected>>", lambda _e: self._load_scenario(
                keep_maze=(_e.widget is not scenario_box)))
            if var is self.scenario_var:
                scenario_box = box
        ttk.Checkbutton(bar, text="Reinicios aleatorios", variable=self.restart_var,
                        command=lambda: self._load_scenario(keep_maze=True)).pack(side="left", padx=8)

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Button(controls, text="Paso", style="Pink.TButton", command=self._do_step).pack(side="left")
        self.auto_btn = ttk.Button(controls, text="Auto", style="Pink.TButton", command=self._toggle_auto)
        self.auto_btn.pack(side="left", padx=6)
        ttk.Button(controls, text="Reiniciar caso", style="Soft.TButton",
                   command=lambda: self._load_scenario()).pack(side="left")
        ttk.Button(controls, text="Ejecutar métricas", style="Soft.TButton",
                   command=self._run_metrics).pack(side="left", padx=6)
        ttk.Label(controls, text="Velocidad").pack(side="left", padx=(18, 4))
        self.speed = tk.DoubleVar(value=250)
        ttk.Scale(controls, from_=600, to=60, variable=self.speed, length=120).pack(side="left")

        body = ttk.Frame(self)
        body.pack(padx=16, pady=4)
        left = card(body, padx=8, pady=8)
        left.grid(row=0, column=0, sticky="n")
        self.canvas = MazeCanvas(left, self._toggle_wall)
        self.canvas.pack()
        ttk.Label(left, style="Card.TLabel", foreground=PinkTheme.MUTED,
                  text="Cuadro = inicio · ♥ = meta · Línea = trayectoria · Más oscuro = mayor f(s)"
                  ).pack(anchor="w", pady=(6, 0))
        self.telemetry = TelemetryPanel(body)
        self.telemetry.grid(row=0, column=1, sticky="n", padx=(12, 0))

        self.metrics = MetricsPanel(self)
        self.metrics.pack(fill="x", padx=16, pady=(10, 16))

    # ---- modelo --------------------------------------------------------------
    def _load_scenario(self, keep_maze: bool = False) -> None:
        self._stop_auto()
        if not keep_maze:
            self.maze: Maze = ScenarioCatalog.create(self._scenario_options[self.scenario_var.get()])
        self.fitness: FitnessFunction = self._fitness_options[self.fitness_var.get()]()
        strategy = self._strategy_options[self.strategy_var.get()]()
        policy = RandomRestart(20) if self.restart_var.get() else NoRestart()
        self.climber = HillClimber(self.maze, self.fitness, strategy, policy, random.Random())
        self._refresh(None)

    def _refresh(self, step: Optional[StepResult]) -> None:
        self.canvas.draw(self.maze, self.fitness, self.climber)
        self.telemetry.show(step, self.climber)

    # ---- eventos -------------------------------------------------------------
    def _do_step(self) -> None:
        if self.climber.finished:
            self._stop_auto()
            return
        step = self.climber.step()
        self._refresh(step)
        if self.climber.finished:
            self._stop_auto()

    def _toggle_auto(self) -> None:
        if self._auto_job is not None:
            self._stop_auto()
            return
        self.auto_btn.config(text="Pausa")
        self._tick()

    def _tick(self) -> None:
        self._do_step()
        if not self.climber.finished and self.auto_btn.cget("text") == "Pausa":
            self._auto_job = self.after(int(self.speed.get()), self._tick)

    def _stop_auto(self) -> None:
        if self._auto_job is not None:
            self.after_cancel(self._auto_job)
            self._auto_job = None
        self.auto_btn.config(text="Auto")

    def _toggle_wall(self, pos: Position) -> None:
        if self.maze.toggle_wall(pos):
            self._load_scenario(keep_maze=True)

    def _run_metrics(self) -> None:
        bench = Benchmark(self.maze, self.fitness)
        strategy = self._strategy_options[self.strategy_var.get()]()
        self.metrics.set_results([bench.evaluate(strategy, NoRestart()),
                                  bench.evaluate(strategy, RandomRestart(20))])


def launch() -> None:
    App().mainloop()
