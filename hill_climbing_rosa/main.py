"""Punto de entrada. `python main.py` abre la interfaz rosa; `python main.py cli ...` usa la consola."""
import sys


def run() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from hillclimb.cli import main
        main(sys.argv[2:])
        return
    try:
        from hillclimb.gui import launch
        launch()
    except Exception as exc:  # sin pantalla o sin tkinter
        if exc.__class__.__name__ in ("TclError", "ModuleNotFoundError", "ImportError"):
            print(f"No se pudo abrir la interfaz gráfica ({exc}).\nUsa el modo consola: "
                  "python main.py cli auto --caso B --reinicios")
        else:
            raise


if __name__ == "__main__":
    run()
