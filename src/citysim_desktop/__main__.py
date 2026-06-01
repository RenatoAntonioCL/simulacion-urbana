"""Punto de entrada del cliente de escritorio:

    python -m citysim_desktop            # abre la ventana
    python -m citysim_desktop --smoke    # arranque headless de validación, sale 0

La vista (Pygame) se importa aquí, no al importar el paquete, para que el controlador
pueda usarse y testearse sin pygame ni display. El parseo de argumentos tampoco importa
pygame: solo se importa la vista al momento de ejecutar.
"""

from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="citysim_desktop", description="Simulación urbana — interfaz de escritorio")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="arranque headless de validación (crea un mundo, avanza y sale 0)",
    )
    args = parser.parse_args(argv)

    if args.smoke:
        # SDL en modo dummy: ni ventana ni audio. Debe fijarse antes de inicializar la vista.
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    try:
        from . import view
    except ImportError:
        sys.stderr.write(
            "Falta Pygame. Instala el extra de interfaz:\n"
            '    pip install ".[ui]"\n'
        )
        raise SystemExit(1)

    if args.smoke:
        view.run_smoke()
    else:
        view.main()


if __name__ == "__main__":
    main()
