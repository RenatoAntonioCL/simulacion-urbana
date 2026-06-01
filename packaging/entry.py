"""Script de arranque para PyInstaller (ADR-0013).

PyInstaller necesita un script como punto de entrada, no `python -m`. Este delega en el
`main` del paquete, de modo que el ejecutable acepta los mismos argumentos (incluido
`--smoke`) que `python -m citysim_desktop`.
"""

from __future__ import annotations

from citysim_desktop.__main__ import main

if __name__ == "__main__":
    main()
