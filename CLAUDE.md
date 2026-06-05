# Project Context for Claude Code

## Project
society-sim — persistent urban simulation: a city that evolves on its own over time,
generating emergent phenomena from simple rules. Not a video game: an artificial society.

## Owner
Renato Antonio — https://github.com/RenatoAntonioCL/how-i-work

## Stack
Python 3.11+ · `dataclasses` · seeded/injected RNG · JSON persistence · `pytest`.
Pygame (optional, desktop client) · PyInstaller (optional, executables).
Docker (multi-stage) · GitHub Actions. Core has zero runtime dependencies (ADR-0009).

## Structure
- `src/citysim/` — simulation engine: `state/` (data only), `systems/` (logic),
  `scheduler/`, `eventlog/`, `seed/`, `projector/`, `facade/` (public API).
- `src/citysim_desktop/` — Pygame client: `controller` (presenter, no pygame) + `view`.
- `tests/` — invariant, determinism, facade and per-week gate tests.
- `Dockerfile`, `docker-compose.yml`, `Makefile`, `packaging/` (PyInstaller spec).
- Docs: `CONTEXT.md`, `ARCHITECTURE.md`, `DECISIONS.md` (ADRs), `ROADMAP.md`, `CHANGELOG.md`.

## Non-negotiables
- Branch protection on main — no direct pushes
- CI must be green before merge
- Tests must pass before merge
- No secrets in code — use environment variables
- Every significant decision gets an ADR
- Semantic versioning

## Conventions
- Commit format: type(scope): description (Conventional Commits)
- Branch format: feat/description, fix/description, docs/description
- PR template: .github/pull_request_template.md
- Commits NEVER include `Co-Authored-By` lines (no Claude/AI co-author) — ever

## Current focus
Week 4 — Society: `Relationship` entity, social contagion (moods spread through the
network), emergent death + consequence queue, offline projection (`projector`) and a
first observer view. Gate: a well-connected death ripples through network and economy.

## What to avoid
- Systems mutating state directly — they emit `Event`; only `eventlog/apply.py` applies (ADR-0001).
- The global `random` — all randomness goes through the injected RNG (ADR-0002).
- Logic in `state/` — `state/` is data only; logic lives in `systems/` (ADR-0003).
- Activating multiple layers at once — validate one at a time to tell emergence from bugs (ADR-0005).
- Letting the economy grow and steal focus — keep it minimal in the MVP.
- Advancing on a broken foundation — if an invariant test fails, stop and fix it first.
