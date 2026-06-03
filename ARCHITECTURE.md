# Architecture — Persistent Urban Simulation (v2)

> Technical reference document. Describes **how** what `simulacion_urbana_v2.md`
> defines as vision and `plan_4_semanas.md` defines as plan is built.
> For the **why** behind each structural decision, see [DECISIONS.md](./DECISIONS.md).

---

## 1. Architectural goal

Build a social simulation engine that is, in this order of priority:

1. **Deterministic** — same `seed` ⇒ same run, bit for bit. Without this there is no
   way to distinguish an emergent phenomenon from a bug.
2. **Auditable** — every state change goes through an `Event`. It is always possible
   to answer *why* something changed.
3. **Layer-replaceable** — each system is a pure function activatable by flag.
   The MVP runs with Layer 1; the rest is toggled without rewriting the core.
4. **Heterogeneous** — agents differ by trait (fixed) + memory (accumulates) +
   emotion (decays), not by different numbers from the same mold.

Performance is **not** an MVP goal (100 agents). Iteration speed and clarity are
prioritized. The architecture is portable: if a bottleneck appears, the core can be
rewritten without touching the design.

---

## 2. High-level view

```text
                         ┌──────────────────────────────────────────┐
                         │                scheduler/                 │
                         │  Multi-scale clock. Orchestrates order.   │
                         └───────────────────┬──────────────────────┘
                                             │ for each tick, in order
                                             ▼
   ┌─────────────┐  reads  ┌──────────────────────────┐  emits   ┌──────────────┐
   │   state/    │ ──────▶ │         systems/         │ ───────▶ │  eventlog/   │
   │  pure data  │         │ rules = pure functions   │  Events  │ applies+saves│
   │ (no logic)  │ ◀────── │ (state) -> [Event]       │          │    events    │
   └─────────────┘ applies └──────────────────────────┘          └──────┬───────┘
          ▲          events                                              │
          └──────────────────────────────────────────────────────────────┘
                         the eventlog is the ONLY component that mutates state

   ┌─────────────┐                                   ┌──────────────────────────┐
   │ projector/  │  (Week 4) offline jump             │        observers/        │
   │ projection  │  deterministic + stochastic        │ read-only views (by role)│
   └─────────────┘                                   └──────────────────────────┘
```

**Flow invariant:** no `system` mutates `state` directly. A system **reads** state
and **returns** a list of `Event`. The `eventlog` is the only component with write
access to state. This provides auditability, reproducibility and, later, the
foundation for offline projection.

**Core / facade / client rings (ADR-0011):** everything above is the **core**.
Around it, `facade/` exposes a stable surface (create, advance, read, save, load)
that delivers read-only DTOs. **Clients** (a desktop UI today; a graphics engine
tomorrow) speak **only** with the facade; they never import `systems/` or touch the
`World`. Dependencies point inward: the core knows nothing about the outside.

The first client is **`citysim_desktop/`** (Pygame, ADR-0012), a package separate
from the core. Internally split into *presenter* (pure Python, no pygame, testable
without a display) and *view* (Pygame). Pygame is an optional dependency
(`pip install ".[ui]"`).

That client is packaged into downloadable executables (Win/Mac/Linux) with PyInstaller
(ADR-0013): the `.spec` and entry script live in **`packaging/`**, outside `src/`,
and a workflow builds one binary per OS. This is build tooling, not part of the engine.

---

## 3. Package structure

```text
src/citysim/
├── rng.py            Seeded RNG, injected. Global random is never used.
├── config.py         Layer flags, run parameters, seed.
│
├── state/            Pure data models. No business logic.
│   ├── world.py          Root container: indexes of all entities + clock.
│   ├── person.py         Person: base state + traits + needs + memory + goals.
│   ├── household.py      Household: members, income, expenses, dwelling.
│   ├── place.py          Place: capacity, schedule, type, location.
│   ├── event.py          Event: type, payload, tick, scale. Source of truth.
│   ├── relationship.py   Relationship: type, strength, reciprocity, history.
│   └── enums.py          Closed types (PlaceType, EventType, RelType, TimeScale).
│
├── systems/          The rules. Pure functions: (world, ctx) -> list[Event].
│   ├── base.py           System protocol + registry by layer/scale.
│   ├── aging.py          Aging, energy, base demographics. (Layer 1)
│   ├── needs.py          Recalculates psychological needs. (Layer 1)
│   ├── wellbeing.py      Wellbeing weighted by traits. (Layer 1)
│   ├── decision.py       Satisficing decision (non-optimizing). (Layer 1/2)
│   ├── economy.py        Work, consumption, household finances. (Layer 2)
│   ├── memory.py         Copies events to episodic memory; decays. (Week 3)
│   ├── emotion.py        Expected-vs-actual appraisal; decaying emotion. (Week 3)
│   ├── goals.py          Goal formation/pursuit/abandonment. (Week 3)
│   ├── relations.py      Creates and updates social bonds. (Week 4 / Layer 4)
│   ├── contagion.py      Network diffusion proportional to bond strength. (Week 4)
│   └── death.py          Accumulated risk + downstream effects. (Week 4)
│
├── scheduler/        The clock.
│   └── clock.py          Multiple scales; system order per tick.
│
├── eventlog/         The registry.
│   ├── log.py            Buffer + persistence of the event history.
│   └── apply.py          Appliers: how each EventType mutates state.
│
├── seed/             Deterministic generation of the initial population.
│   └── seeder.py        100 persons · 30 households · 20 businesses · 1 neighborhood.
│
├── facade/           (ADR-0011) Single public surface for clients.
│   ├── simulation.py    Simulation class: create/advance/read/save/load.
│   └── dto.py           Frozen read-only DTOs (copies of relevant state).
│
├── projector/        (Week 4) Offline persistence: projected state.
│   └── projector.py
│
└── observers/        (Week 4) Read-only views by role.
    └── citizen.py        Single view for the MVP.
```

---

## 4. Data model (state/)

Pure models with `@dataclass`. **No business methods**: logic lives in `systems/`.
This makes them trivial to serialize, copy and test.

### Time scales of `Person` attributes

Heterogeneity arises from combining three distinct scales (see table in the vision):

| Concept      | Nature                    | Stored?               | Lives in `Person`              |
|--------------|---------------------------|-----------------------|--------------------------------|
| **Trait**    | Stable, nearly invariant  | Yes, as a constant    | `traits` (set at birth)        |
| **Memory**   | Accumulative, slow decay  | Yes, as a record      | `memory: list[MemoryTrace]`    |
| **Emotion**  | Transient, fast decay     | **Never stored**      | **recomputed** every tick      |

> Hard rule: **arbitrary psychological states are not stored**. "Sad person" is
> forbidden. Emotion is a derived signal that is recomputed; never a persisted field.
> See `systems/emotion.py` and [DECISIONS.md → ADR-0006](./DECISIONS.md).

### Entity identity

Every entity has a stable `id` (integer assigned by the seeder/RNG). References
between entities are made **by id**, never by direct pointer, so that state is
serializable and referential integrity is testable.

---

## 5. Systems (systems/)

A `System` is a pure function with the signature:

```python
def step(world: World, ctx: TickContext) -> list[Event]: ...
```

- **Does not mutate** `world`. Reads and returns events.
- Is **deterministic**: all randomness comes from `ctx.rng`, never from global `random`.
- Declares its **scale** (hourly/daily/monthly/population) and its **layer** (1–6).
- Registered in `systems/base.py`; the scheduler decides which ones run based on
  the current tick's scale and active layer flags.

The **order** within an hourly tick follows the agent loop from the vision:

```text
1. aging/needs      Update state (incl. recalculate and decay emotion).
2. emotion          Evaluation (appraisal): expected vs actual -> emotion.
3. decision         Choose action (satisficing, biased by traits + emotion).
4. (execution)      The action is emitted as an Event.
5. memory/relations Process events -> episodic memory + social network.
6. economy/...      Household, economy and mobility at their respective scale.
```

**Currently active systems** (`build_default_registry`): `aging` (population) and,
from Week 2, `needs` → `wellbeing` → `decision` → `economy` (hourly, Layer 1, in
that order). `emotion`, `memory`, `relations`, etc. are registered in Weeks 3–4.

---

## 6. Clock (scheduler/)

v1 fixed "1 tick = 1 hour". v2 uses **multiple scales**: the scheduler advances in
hourly ticks and fires the larger scales when appropriate.

```text
Hourly tick        → individual behavior, energy, routines
Daily step         → household finances, contracts
Monthly step       → aggregate economy, labor market
Population step    → demographics (births, deaths, aging)
```

At each boundary (end of day, end of month, etc.) the scheduler runs the systems
registered for that scale, in layer order. One MVP year = 365 days of ticks.

---

## 7. Events and eventlog (eventlog/)

- An `Event` is an immutable datum: `(type, tick, scale, payload)`.
- Systems **emit** events; they never apply changes.
- `eventlog/apply.py` has one applier per `EventType` that knows how that event
  mutates the `world`. It is the only place with write access.
- `eventlog/log.py` stores the complete history (source of truth for the run).
- **NEW (v2):** significant events for an agent are also copied to its episodic
  memory (done by `systems/memory.py` reading the tick's log).

This pattern enables: reproducibility, causal auditability, and offline projection
(which reconstructs/skips state based on the nature of the processes).

---

## 8. Determinism and randomness (rng.py)

- **A single** `random.Random(seed)` is created at startup and injected via
  `TickContext`. Nothing uses global `random`.
- For reproducible sub-streams (e.g. per system), child generators are derived
  deterministically from the master seed, not via ad-hoc instances.
- Consequence: two runs with the same seed produce **the same event log**, which is
  exactly the Week 1 validation gate.

---

## 9. Offline persistence (projector/) — Week 4

The biggest technical risk. On reconnection, the absent time is **not** simulated
tick by tick: a consistent state is projected by separating processes by nature.

```text
Deterministic (computable in a jump):
  aging, contracts, recurring payments, base demographics

Stochastic (sampled, not simulated tick by tick):
  accidents, social encounters, acute health events
```

---

## 10. Invariant tests (the anti-debt backbone)

Properties that must **never** be violated, checked on every run. If one fails,
stop and fix it: no debt accumulates.

1. **Money conservation** — money does not appear or disappear without an event explaining it.
2. **Population balance** — alive + dead = born. No leaks.
3. **Valid ranges** — energy, wellbeing, health ∈ `[0, 1]`; age ≥ 0.
4. **Referential integrity** — every relationship/household points to existing entities.
5. **Determinism** — two runs with the same seed ⇒ identical event logs.

Implemented in `tests/` with `pytest`. See [CONTEXT.md](./CONTEXT.md) for coverage
status per week.

---

## 11. Activatable layers (not phases)

Layers are **flags**, not sequential code stages. The engine knows nothing about
layers; it simply activates the systems whose flag is on.

```text
Layer 1  Persons · Households · Work · Mobility          ← MVP starts here
Layer 2  Income · Expenses · Savings · Commerce
Layer 3  Climate · Energy · Water · Gas · Electricity
Layer 4  Relationships · Friendships · Partners · Support networks
Layer 5  Physical health · Mental health · Habits
Layer 6  Safety · Accidents · Violations · Patrols · Cameras
```

---

## 12. Plan → architecture map

| Week | Validation gate                                         | Components touched                                          |
|------|---------------------------------------------------------|-------------------------------------------------------------|
| 1    | Does the world tick deterministically and reproducibly? | `rng`, `state/*`, `eventlog`, `scheduler`, `seeder`         |
| 2    | Do agents look distinct from each other?                | `traits`, `needs`, `wellbeing`, `decision`, `economy`       |
| 3    | Does the past weigh in? Is there credible irrationality?| `memory`, `emotion`, `goals`                                |
| 4    | Does the network react to a death/shock?                | `relations`, `contagion`, `death`, `projector`, `observers` |

---

## 13. Scalability principles (preserved)

Do not simulate everything at maximum detail. Levels of abstraction:

```text
Level 1  Aggregate statistics
Level 2  Households
Level 3  Individual persons
Level 4  Active persons near the user
```

Complexity only increases when necessary. Not implemented in the MVP, but the
design (entities by id, systems by layer) does not prevent it.
