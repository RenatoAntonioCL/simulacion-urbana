"""observers/ — vistas de solo-lectura sobre el estado, según el rol (Semana 4).

La simulación es única; las vistas cambian. El MVP incluye una sola (Ciudadano).
"""

from .citizen import CitizenView

__all__ = ["CitizenView"]
