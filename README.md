# Persistent Urban Simulation

[![CI](https://github.com/RenatoAntonioCL/society-sim/actions/workflows/ci.yml/badge.svg)](https://github.com/RenatoAntonioCL/society-sim/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

A city that evolves on its own over time, generating emergent phenomena from
simple rules. It is not a video game: it is an **artificial society**.

> The city does not exist for the player. The player exists inside the city.

## Documentation

| Document | Content |
|---|---|
| [`simulacion_urbana_v2.md`](./simulacion_urbana_v2.md) | Vision and conceptual model |
| [`plan_4_semanas.md`](./plan_4_semanas.md) | MVP execution plan (weekly gates) |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Technical architecture |
| [`DECISIONS.md`](./DECISIONS.md) | Architecture decisions (ADRs) |
| [`ROADMAP.md`](./ROADMAP.md) | Milestones toward alpha versions and progress |
| [`CONTEXT.md`](./CONTEXT.md) | Live status and working conventions |
| [`CHANGELOG.md`](./CHANGELOG.md) | Change history |

## Stack

Python 3.11+ · `dataclasses` · `pytest` · seeded RNG · JSON persistence.
Minimal dependencies. (See [ADR-0009](./DECISIONS.md).)

## Structure

```text
src/citysim/      Simulation engine (see ARCHITECTURE.md §3)
tests/            Invariant and behavior tests
Dockerfile        Multi-stage image (build / test / runtime non-root)
docker-compose.yml  `sim` and `tests` services
Makefile          Shortcuts: build, run, test, shell
```

## Getting started

### With Docker (recommended)

No Python installation required: Docker only.

```bash
make build        # builds the runtime image
make run          # runs the simulation (vars: DAYS=30 SEED=7)
make test         # runs the test suite inside the container
make shell        # opens a shell inside the container
make help         # lists all targets
```

Or directly with the Docker / Compose CLI:

```bash
docker build -t citysim .
docker run --rm citysim --days 30 --seed 7

docker compose run --rm sim --days 30   # run
docker compose run --rm tests           # pytest suite
```

The image is multi-stage (build / test / runtime), runs as a non-root user and
the final image weighs ~220 MB. See [`Dockerfile`](./Dockerfile).

### Local (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m citysim --days 30
```

### Desktop interface (Pygame)

Visual client: create a world, watch it, control the clock (play/pause, speed, step)
and save/load. Pygame is an optional dependency; the core does not require it.

```bash
pip install -e ".[ui]"
python -m citysim_desktop
```

### Desktop application (executable)

To use without installing Python, downloadable executables are available for Windows,
macOS and Linux: they are built by the **Package** workflow (manually or when publishing
a `vX.Y.Z` tag) and are attached as *artifacts* or to the corresponding *Release*.

To build the executable locally (output in `dist/`):

```bash
pip install -e ".[ui,build]"
pyinstaller packaging/citysim-desktop.spec
./dist/citysim-desktop            # or dist/citysim-desktop.exe on Windows
```

> Binaries are unsigned: macOS (Gatekeeper) and Windows (SmartScreen) may ask for
> confirmation when opening them for the first time. See [ADR-0013](./DECISIONS.md).

## Status

**`v0.3.0-alpha` — Week 3 (Trajectory).** The deterministic core runs, agents have
traits, needs, wellbeing, a satisficing decision, a minimal economy and now memory,
transient emotion and dynamic goals: past lived experience changes present behavior.
A Pygame desktop client lets you create a world and watch it evolve (play/pause, speed,
step, save/load). 49 green tests. Next: Week 4 (Society — relationships, contagion,
death). See [CONTEXT.md](./CONTEXT.md) for live status.

## Principles

1. **Deterministic** — same seed ⇒ same run.
2. **Auditable** — every change goes through an `Event`.
3. **Layered** — the MVP runs with Layer 1; the rest is toggled by flags.
4. **Heterogeneous** — trait (fixed) + memory (accumulates) + emotion (decays).
