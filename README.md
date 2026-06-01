# Simulación Urbana Persistente

[![CI](https://github.com/RenatoAntonioCL/simulacion-urbana/actions/workflows/ci.yml/badge.svg)](https://github.com/RenatoAntonioCL/simulacion-urbana/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

Una ciudad que evoluciona sola en el tiempo, generando fenómenos emergentes a partir
de reglas simples. No es un videojuego: es una **sociedad artificial**.

> La ciudad no existe para el jugador. El jugador existe dentro de la ciudad.

## Documentación

| Documento | Contenido |
|---|---|
| [`simulacion_urbana_v2.md`](./simulacion_urbana_v2.md) | Visión y modelo conceptual |
| [`plan_4_semanas.md`](./plan_4_semanas.md) | Plan de ejecución del MVP (gates semanales) |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Arquitectura técnica |
| [`DECISIONS.md`](./DECISIONS.md) | Decisiones de arquitectura (ADRs) |
| [`ROADMAP.md`](./ROADMAP.md) | Hitos hacia las versiones alpha y progreso |
| [`CONTEXT.md`](./CONTEXT.md) | Estado vivo y convenciones de trabajo |
| [`CHANGELOG.md`](./CHANGELOG.md) | Historial de cambios |

## Stack

Python 3.11+ · `dataclasses` · `pytest` · RNG sembrado · persistencia JSON.
Dependencias mínimas. (Ver [ADR-0009](./DECISIONS.md).)

## Estructura

```text
src/citysim/      Motor de simulación (ver ARCHITECTURE.md §3)
tests/            Tests de invariantes y de comportamiento
Dockerfile        Imagen multi-stage (build / test / runtime no-root)
docker-compose.yml  Servicios `sim` y `tests`
Makefile          Atajos: build, run, test, shell
```

## Puesta en marcha

### Con Docker (recomendado)

No requiere tener Python instalado: solo Docker.

```bash
make build        # construye la imagen de ejecución
make run          # corre la simulación (vars: DAYS=30 SEED=7)
make test         # corre la suite de tests dentro del contenedor
make shell        # abre una shell dentro del contenedor
make help         # lista todos los objetivos
```

O directamente con la CLI de Docker / Compose:

```bash
docker build -t citysim .
docker run --rm citysim --days 30 --seed 7

docker compose run --rm sim --days 30   # ejecución
docker compose run --rm tests           # suite de pytest
```

La imagen es multi-stage (build / test / runtime), corre como usuario no-root y la
final pesa ~220 MB. Ver [`Dockerfile`](./Dockerfile).

### Local (sin Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m citysim --days 30
```

## Estado

**Semana 0 — Scaffolding.** Estructura y contratos creados; sin lógica de simulación
todavía. Próximo: Semana 1 (núcleo determinista). Ver [CONTEXT.md](./CONTEXT.md).

## Principios

1. **Determinista** — mismo seed ⇒ mismo run.
2. **Auditable** — todo cambio pasa por un `Event`.
3. **Por capas** — el MVP corre con la Capa 1; el resto se enciende por flags.
4. **Heterogéneo** — rasgo (fijo) + memoria (acumula) + emoción (decae).
