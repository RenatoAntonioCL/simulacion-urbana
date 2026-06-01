"""Punto de entrada del cliente de escritorio:

    python -m citysim_desktop

La vista (Pygame) se importa aquí, no al importar el paquete, para que el controlador
pueda usarse y testearse sin pygame ni display.
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from .view import main as run_app
    except ImportError:
        sys.stderr.write(
            "Falta Pygame. Instala el extra de interfaz:\n"
            '    pip install ".[ui]"\n'
        )
        raise SystemExit(1)
    run_app()


if __name__ == "__main__":
    main()
