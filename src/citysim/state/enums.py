"""Tipos cerrados del dominio: escalas de tiempo, capas, tipos de lugar/relación/evento."""

from __future__ import annotations

from enum import Enum


class TimeScale(Enum):
    """Escalas del reloj multi-escala (ADR-0008)."""

    HOURLY = "hourly"          # conducta individual, energía, rutinas
    DAILY = "daily"            # finanzas del hogar, contratos
    MONTHLY = "monthly"        # economía agregada, mercado laboral
    POPULATION = "population"  # demografía: nacimientos, muertes, envejecimiento


class Layer(Enum):
    """Capas activables (ADR-0005). El MVP usa solo L1_BASE."""

    L1_BASE = 1        # Personas · Hogares · Trabajo · Movilidad
    L2_ECONOMY = 2     # Ingresos · Gastos · Ahorro · Comercio
    L3_ENERGY = 3      # Clima · Energía · Agua · Gas · Electricidad
    L4_RELATIONS = 4   # Relaciones · Amistades · Parejas · Redes de apoyo
    L5_HEALTH = 5      # Salud física · Salud mental · Hábitos
    L6_SECURITY = 6    # Seguridad · Accidentes · Infracciones · Patrullas


class PlaceType(Enum):
    HOME = "home"
    BUSINESS = "business"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    SHOP = "shop"
    PARK = "park"


class RelType(Enum):
    FAMILY = "family"
    FRIEND = "friend"
    PARTNER = "partner"
    WORK = "work"


class EventType(Enum):
    """Tipos de evento (fuente de verdad — ADR-0001). Se amplía por semana/capa."""

    # Semana 1 — demografía base / tiempo
    TICK = "tick"
    BIRTH = "birth"
    DEATH = "death"
    AGED = "aged"

    # Semana 2 — economía mínima
    INCOME = "income"
    EXPENSE = "expense"
    ACTION_CHOSEN = "action_chosen"

    # Semana 3 — trayectoria
    GOAL_FORMED = "goal_formed"
    GOAL_ACHIEVED = "goal_achieved"
    GOAL_ABANDONED = "goal_abandoned"

    # Semana 4 — sociedad
    RELATIONSHIP_FORMED = "relationship_formed"
    RELATIONSHIP_CHANGED = "relationship_changed"
    MOVED = "moved"
    INHERITANCE = "inheritance"
