"""citysim_desktop — primer cliente visual de la simulación (ADR-0011).

Cliente de escritorio en Pygame. **Fuera** del paquete núcleo: consume solo
`citysim.facade`. Importar este paquete NO requiere pygame (la vista se carga aparte,
en `citysim_desktop.view`, desde `__main__`); así el controlador puede usarse y testearse
sin display.

    python -m citysim_desktop
"""

from __future__ import annotations

from .controller import SimController

__all__ = ["SimController"]
