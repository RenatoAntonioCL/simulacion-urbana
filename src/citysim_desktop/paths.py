"""paths — ubicación de datos del usuario, multiplataforma (sin pygame).

En un ejecutable lanzado con doble clic, el directorio de trabajo no es confiable: no se
puede guardar junto al binario. Por eso los mundos guardados van a un directorio de datos
del usuario, propio de cada SO. Python puro, sin dependencias: testeable sin display.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "citysim"


def user_data_dir(app: str = APP_NAME) -> Path:
    """Directorio de datos del usuario para `app`, creado si no existe.

    - Windows: %APPDATA%\\<app>
    - macOS:   ~/Library/Application Support/<app>
    - Linux/otros: $XDG_DATA_HOME/<app> o ~/.local/share/<app>
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share")

    path = Path(base) / app
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_save_path(app: str = APP_NAME) -> Path:
    """Ruta del archivo de guardado por defecto, en el directorio de datos del usuario."""
    return user_data_dir(app) / "world_save.json"
