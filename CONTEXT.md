# Project Context

> Live status of the project: where we are, what comes next, and how to work here.
> Updated at the close of each week/milestone. Last updated: **2026-06-02**.

---

## What this is

A **persistent urban simulation**: a city that evolves autonomously over time, even
while the user is offline. The goal is not a video game but an **artificial society**
that generates emergent phenomena (mobility, economy, relationships, health, death).
The city is the protagonist.

> The city does not exist for the player. The player exists inside the city.

Source documents:
- **`simulacion_urbana_v2.md`** — vision and conceptual model (the *what* and *why*).
- **`plan_4_semanas.md`** — MVP execution plan with weekly gates.
- **`ARCHITECTURE.md`** — how it is built technically.
- **`DECISIONS.md`** — architecture decisions (ADRs) with their rationale.
- **`CHANGELOG.md`** — what changed and when.

---

## Current status

| Aspect              | Status                                                              |
|---------------------|---------------------------------------------------------------------|
| Phase               | **Week 3 — Trajectory** (memory + emotion + goals)                 |
| Week 1 (Core)       | 🟡 In progress: engine beats, ticks and records events             |
| Week 2 (Identity)   | ✅ Traits, needs, wellbeing, decision, economy (v0.2.0-alpha)      |
| Week 3 (Trajectory) | ✅ Episodic memory, transient emotion, dynamic goals (v0.3.0-alpha)|
| Week 4 (Society)    | ⬜ Pending                                                         |
| Platform            | ✅ Facade + Pygame client + executables (release v0.1.0)           |
| Active layers       | Layer 1 (Persons · Households · Work · Mobility · minimal economy) |
| Tests               | ✅ 49 green tests (invariants, reproducibility, facade, UI, gates Wk 2 & 3) |

Legend: ✅ done · 🟡 in progress · ⏳ next · ⬜ pending

### What EXISTS and WORKS today
- Architecture, decisions, context and changelog documentation.
- `src/citysim/` package with the full contract (state, systems, scheduler, eventlog,
  seed, projector, observers).
- **Running deterministic core**: `python -m citysim --days 30` seeds 100
  persons · 30 households · 50 places, ticks one month and records ~3.7k events.
- Seeded and injected RNG; eventlog that applies and persists; multi-scale scheduler;
  deterministic seeder; example `aging` system.
- `invariants.py` + `tests/` (7 green tests): population balance, valid ranges,
  referential integrity and seed reproducibility.
- **Full Dockerization**: multi-stage `Dockerfile` (build/test/runtime non-root),
  `docker-compose.yml`, `Makefile` and `.dockerignore`. `make build/run/test` work;
  container run reproduces the same log fingerprint as local.

### What is still a STUB (deliberate NotImplementedError)
- Week 4 systems: `relations`, `contagion`, `death`.
- Offline projection (`projector`) and observers (Week 4).

> Note on determinism: with only `aging` (seed-independent), the event log does not yet
> diverge between seeds; the seed today only affects the initial population. Log
> divergence by seed will come with the stochastic systems. The test documents this
> and will need to be strengthened at that point.

---

## Immediate next step

Start **Week 4 — Society** (relationships, contagion, death):
1. `Relationship` entity with type, strength, reciprocity and history.
2. Social contagion: moods spread through the network (proportional to link strength).
3. Emergent death system + consequence queue (grief, inheritance, household restructuring).
4. Offline projection (`projector`) and one observer view.

**Week 4 gate:** a well-connected death generates ripples in the network and economy;
a neighborhood shock produces a collective mood drop.

---

## MVP scale

```text
100 persons · 30 households · 20 businesses · 1 neighborhood · 1 simulated year
```

---

## Working conventions

- **Determinism first.** All randomness goes through the injected RNG. Never the
  global `random`. (ADR-0002)
- **Events for every change.** Systems do not mutate state; they emit `Event`. Only
  the `eventlog` applies. (ADR-0001)
- **`state/` is data only.** Logic goes in `systems/`. (ADR-0003)
- **Do not advance with a broken foundation.** If an invariant test fails, stop and
  fix it. No debt accumulates.
- **Do not activate layers all at once.** Validate one at a time to distinguish
  emergence from bugs. (ADR-0005)
- **Agent richness is the priority.** Keep the economy minimal in the MVP;
  don't let it consume the focus.

## Language
- Documentation and comments: **English**.
- Code identifiers: **English** (`Person`, `Household`, `decide_action`).

---

## Active risks

- **Offline projection** — the biggest technical risk; addressed in Week 4.
- **Premature over-engineering** — at 100 agents, optimizing wastes time.
- **Absorbing economy** — tends to grow and steal focus; keep it minimal.
- **Skipping a gate** — without validating each milestone, emergence cannot be
  distinguished from bugs.
