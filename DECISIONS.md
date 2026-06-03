# Architecture Decision Records (ADR)

> Each significant structural decision is recorded here with its context and
> consequences. Lightweight ADR-style format. The **what** is in
> [ARCHITECTURE.md](./ARCHITECTURE.md); the **why** lives here.

Possible states: `Proposed` · `Accepted` · `Superseded by ADR-XXXX` · `Obsolete`.

---

## ADR-0001 — Events as the single source of truth

- **Status:** Accepted
- **Context:** If each system mutates state on its own, it is impossible to audit why
  something changed, reproduce bugs or build the offline projection.
- **Decision:** No system mutates state. Systems **emit** `Event`; only
  `eventlog/apply.py` applies events to the `World`.
- **Consequences:**
  - (+) Full causal auditability; reproducibility; foundation for offline projection.
  - (+) Each change is testable in isolation (event → expected effect).
  - (−) More verbose: every change requires defining an `EventType` and its applier.
  - (−) Care needed with application order within a tick (fixed by the scheduler).

---

## ADR-0002 — Determinism with a single seeded and injected RNG

- **Status:** Accepted
- **Context:** The project needs to distinguish genuine emergence from bugs. Without
  exact reproducibility, that is impossible.
- **Decision:** A single `random.Random(seed)` created at startup and injected via
  `TickContext`. Global `random` or ad-hoc instances are forbidden. Sub-streams are
  derived deterministically from the master seed.
- **Consequences:**
  - (+) Same seed ⇒ same event log, bit for bit. Reproducible bugs.
  - (−) Permanent discipline: any stray `import random` breaks the guarantee
    (monitored in review and, ideally, with a test/lint).

---

## ADR-0003 — `state/` is pure data; logic lives in `systems/`

- **Status:** Accepted
- **Context:** Mixing data and behavior in entities makes it harder to serialize,
  test and replace rules.
- **Decision:** Entities are `dataclass` with no business methods. Every rule is a
  pure function in `systems/` with signature `(World, TickContext) -> list[Event]`.
- **Consequences:**
  - (+) Trivial serialization (JSON), simple tests, interchangeable rules.
  - (+) Fits ADR-0001: systems cannot mutate because they have no methods.
  - (−) Some ergonomic friction (no `person.work()`).

---

## ADR-0004 — References between entities by `id`, not by pointer

- **Status:** Accepted
- **Context:** State must be serializable and referential integrity must be testable.
- **Decision:** Every entity has a stable `id`. Relationships, households and places
  reference other entities by `id`. The `World` maintains the indexes.
- **Consequences:**
  - (+) Serializable state; referential integrity invariant is checkable.
  - (−) Indirection: ids must be resolved against the `World` indexes.

---

## ADR-0005 — Layers as activatable flags, not code phases

- **Status:** Accepted
- **Context:** The vision defines 6 layers. Treating them as sequential phases would
  require rewriting the engine to activate each one.
- **Decision:** The engine knows nothing about layers. Each system declares its layer;
  the scheduler runs only the systems whose flag is active in `config.py`.
- **Consequences:**
  - (+) The MVP is validated with Layer 1 and the rest is toggled without touching the core.
  - (+) Allows isolating variables when debugging emergence (activate one at a time).
  - (−) Flags and inter-layer dependencies must be kept consistent.

---

## ADR-0006 — Three scales of psychological state: trait / memory / emotion

- **Status:** Accepted
- **Context:** v1 produced flat agents and banned "arbitrary psychological states".
  Depth must be added without violating that prohibition.
- **Decision:** Separate by time scale:
  - **Trait** — constant set at birth; stored.
  - **Memory** — accumulative record that decays slowly; stored.
  - **Emotion** — transient signal derived from appraisal; **never stored**, recomputed
    every tick and decaying at a rate set by resilience.
- **Consequences:**
  - (+) Persisted "sad person" remains forbidden; grief emerges and decays.
  - (+) Two identical agents today act differently because of their different memory.
  - (−) Emotion recomputed every tick has a cost; acceptable at MVP scale.

---

## ADR-0007 — Satisficing decision, not global optimization

- **Status:** Accepted
- **Context:** Perfect global optimizers look robotic and identical.
- **Decision:** Agents choose the first option that is "good enough" according to their
  personal weights, with incomplete information and emotional bias, subject to money,
  time and energy constraints.
- **Consequences:**
  - (+) Behavioral diversity; bounded irrationality reads as humanity.
  - (+) Cheaper than optimizing over the full action space.
  - (−) The "good enough" threshold is a parameter that needs calibration.

---

## ADR-0008 — Multi-scale clock instead of "1 tick = 1 hour"

- **Status:** Accepted
- **Context:** Different processes (behavior vs. demographics) occur at very different
  rates; simulating everything at hourly scale is wasteful and unnatural.
- **Decision:** The scheduler advances in hourly ticks and fires daily, monthly and
  population scales at their boundaries, running the systems for each scale.
- **Consequences:**
  - (+) Efficiency and more faithful modeling; fits with offline projection.
  - (−) Order and boundaries between scales must be kept explicit.

---

## ADR-0009 — Stack: Python 3.11+ with minimal dependencies, JSON first

- **Status:** Accepted
- **Context:** At 100 agents performance is not the problem; iteration speed is. The
  core must be portable in case a bottleneck appears later.
- **Decision:** Python 3.11+, `dataclasses`, `pytest`, seeded RNG, JSON persistence
  (SQLite if querying is needed). No heavy simulation frameworks.
- **Consequences:**
  - (+) Fast iteration; low barrier to entry; portable design.
  - (−) Future core rewrite if scaled significantly (assumed and accepted).

---

## ADR-0010 — Death is an emergent system with a consequence queue

- **Status:** Accepted
- **Context:** In v1 death would be a `delete` with income adjustment: it carries no weight.
- **Decision:** Death emerges from accumulated health risk (age, habits, stress, healthcare
  access) + acute events, with psychosocial factors as one among several. It triggers
  downstream effects: grief scaled by bond strength, role vacancy, economic shock +
  inheritance, household restructuring, trace in the memory of the living.
- **Consequences:**
  - (+) A death generates ripples in the network and the economy (Week 4 gate).
  - (−) Couples several systems (death, relations, contagion, economy, household);
    requires careful application order via events.

## ADR-0011 — Core / facade / client architecture

- **Status:** Accepted
- **Context:** The project stops being just an engine that outputs a log and becomes a
  **downloadable desktop application** (Windows, macOS, Linux) where each user creates
  and observes their own worlds. The horizon includes connecting a graphics engine
  (Godot/Unity) in the future. If the simulation core and the visual layer are coupled,
  adding or changing the interface would require rewriting the engine. The interface must
  be guaranteed to be a replaceable piece, not a core dependency.
- **Decision:** Three rings with one-directional dependencies (outside-in; the core knows
  nothing about the outside):
  1. **Core** (current `citysim/`: `state`, `systems`, `eventlog`, `scheduler`,
     `seed`, `invariants`, `rng`). Does not change. Its responsibility is advancing the
     simulation and guarding state. It knows nothing about UI, windows or rendering.
  2. **Facade** (`citysim/facade/`): a stable, minimal interface — the **only** surface
     clients may touch. Exposes high-level operations (create world, advance, read state,
     read events, save, load) and delivers **read-only DTOs**, never the internal `World`
     entities. It is the contract that decouples core and clients.
  3. **Clients** (outside the core package): consume only the facade. Today, a desktop UI.
     Tomorrow, Godot/Unity or others. None import from `systems/`, `eventlog/` or touch
     the `World` directly.
- **Consequences:**
  - (+) The UI is replaceable without touching the engine; a future graphics engine
    connects to the same facade (it is, in fact, the bridge toward Godot/Unity).
  - (+) The facade is a natural point for serializing worlds: since the core is
    deterministic and seeded (ADR-0002), a world is defined by `config + seed`, so
    saving/sharing a world is saving/sharing very little. Saving is implemented via
    *replay* (`config + ticks`), avoiding serializing pointers (ADR-0004).
  - (+) Read-only DTOs prevent a client from accidentally corrupting state, preserving
    ADR-0001 (events as the only path for change).
  - (+) Testable: the facade can be exercised without any UI mounted.
  - (−) Extra mapping layer (internal entity → DTO) with some duplication and
    maintenance cost when state changes shape.
  - (−) Permanent discipline: the rule "clients only talk to the facade" must be
    enforced in review; a direct import of `systems/` from a client breaks it.
  - (−) The facade must remain stable; changing it breaks all clients at once, so its
    changes are thought through more carefully than internal ones.

## ADR-0012 — First visual client: Pygame in-process, split into presenter/view

- **Status:** Accepted
- **Context:** With the facade ready (ADR-0011), the first visual interface is next.
  The goal is a downloadable, cross-platform desktop application, with a graphics engine
  (Godot/Unity) on the horizon. A tool for the first client must be chosen, along with
  an internal structure that does not become a dead end. Form-library tools (Tkinter/Qt)
  work for panels, not for drawing a neighborhood with moving things; they clash with
  that horizon. Jumping straight to Godot adds an IPC bridge and a second language
  before anything appears on screen.
- **Decision:** The first client is **Pygame, in-process**, in a package separate from
  the core, `citysim_desktop/`, consuming **only** `citysim.facade` and `citysim.config`.
  Internally split into two:
  1. **Presenter** (`controller.py`, `layout.py`): pure Python, **no pygame**. Manages
     the `Simulation`, translates UI intentions into facade calls and derives the visual
     layout from ids (the core has no coordinates — ADR-0004).
  2. **View** (`view.py`): Pygame. Only draws what the presenter exposes and sends input.
  Pygame is an **optional dependency** (`pip install ".[ui]"`); the core and facade
  remain dependency-free (ADR-0009).
- **Consequences:**
  - (+) Minimal friction to validate the facade with something visible and packagable
    to an executable (PyInstaller) on all three OSes.
  - (+) The presenter, without pygame, is testable without a display (runs in CI without
    a screen); the view remains a replaceable piece. On the day of Godot/Unity, only the
    view changes and the presenter/facade stay the same — the same boundary as ADR-0011,
    one level up.
  - (+) The core gains no dependencies: `import citysim.facade` works without pygame.
  - (−) Pygame has a low graphical ceiling; it is not an engine. The jump to Godot/Unity
    remains separate work (its bridge is the facade).
  - (−) Extra discipline: the view must not leak simulation logic and the client must not
    import from the core beyond the facade (covered by a test).

## ADR-0013 — Executable packaging with PyInstaller, per-OS build in CI

- **Status:** Accepted
- **Context:** The client goal (ADR-0012) is to be a **downloadable** desktop application
  for Windows, macOS and Linux, without requiring the user to install Python. Packaging
  Pygame with PyInstaller has known pitfalls: system fonts may not be in the frozen
  binary, the working directory is unreliable when launched by double-click, and
  PyInstaller does **not** cross-compile.
- **Decision:** Package with **PyInstaller** in **onefile** mode (a single downloadable
  file), with a versioned `.spec` (`packaging/citysim-desktop.spec`) and a thin entry
  script (`packaging/entry.py`). To avoid the pitfalls:
  - **Font:** the view uses **Pygame's built-in font** (`pygame.font.Font(None, …)`),
    which travels with Pygame; no `.ttf` files are bundled and `SysFont` is not used.
    Eliminates the OS font dependency without `--add-data`.
  - **Saving:** worlds are saved in an **OS user data directory**
    (`citysim_desktop/paths.py`), not next to the binary or in the cwd.
  - **Per-OS build:** a `package.yml` workflow with an `ubuntu`/`windows`/`macos`
    matrix builds one binary per platform (PyInstaller does not cross-compile). Each job
    validates the binary with a headless **`--smoke`** mode (`SDL_VIDEODRIVER=dummy`)
    that creates a world, advances it and exits 0; then uploads it as an artifact. On
    `vX.Y.Z` tags, it also attaches it to a GitHub Release.
  - **Trigger:** only `workflow_dispatch` and `v*` tags (not on every PR, to avoid
    burning minutes). PyInstaller is an optional `build` extra; the core remains
    dependency-free (ADR-0009).
- **Consequences:**
  - (+) Downloadable executables for all three OSes, with nothing for the user to install.
  - (+) The `--smoke` mode gives a real signal that the bundle starts on each OS,
    without needing a display in CI.
  - (+) Core and facade untouched and without new dependencies; all the change lives in
    the client and in `packaging/`.
  - (−) Three separate builds (one per OS); no single universal artifact.
  - (−) Binaries are unsigned: macOS/Windows may warn when opening them
    (Gatekeeper/SmartScreen). Signing/notarizing is out of scope for now.
  - (−) onefile starts slightly slower (self-extracts); if this causes issues on some OS,
    the documented fallback in the `.spec` is to switch to onedir.

## ADR-0014 — Identity (Week 2): deterministic decision, action as state, money conserved

- **Status:** Accepted
- **Context:** Week 2 gives agents heterogeneity (traits + needs + wellbeing + decision
  + minimal economy). Three things had to be resolved: where decision diversity comes
  from, how to connect "deciding" with "having economic consequence" without coupling
  systems, and how to prevent money from being created or destroyed.
- **Decision:**
  1. **Deterministic, not stochastic, decision.** The `decision` system chooses the first
     "good enough" action (ADR-0007) scored by traits+needs, without `ctx.rng`. Diversity
     comes from **traits**, which the seeder samples with population-level variation from
     the seeded RNG (ADR-0002). Intended consequence: the log now **diverges by seed**
     (different traits ⇒ different decisions), reinforcing end-to-end determinism without
     per-tick randomness.
  2. **Minimal economy in `L1_BASE`** (as the plan states). Runs in the MVP by default;
     `L2_ECONOMY` is reserved for the richer economy (savings/commerce/investment) of the
     post-MVP.
  3. **`Person.current_action`** as *activity state* (not emotion — ADR-0006 forbids
     persisting mood, not current activity, same as `location_id`). `decision` sets it
     via the `ACTION_CHOSEN` event; `economy` reads it to emit `INCOME`/`EXPENSE`. This
     decouples decision and economy: they communicate via state + events, not direct calls.
  4. **Money conservation** as invariant (#1 of ARCHITECTURE §10): the current total must
     balance against the seeded initial amount plus Σ`INCOME` − Σ`EXPENSE`. Spending is
     capped at what is available (`min(cost, money)`) so the balance is exact.
- **Consequences:**
  - (+) Week 2 gate is verifiable: opposite traits ⇒ different and stable decisions.
  - (+) Stronger and testable determinism (different seeds ⇒ different logs).
  - (+) The economy cannot "manufacture" money without an invariant detecting it.
  - (−) `decision`/`needs`/`wellbeing` emit many events (per person per tick); mitigated
    by emitting needs/wellbeing only on changes ≥ ε, but a year's log is large
    (perf is not an MVP goal — ARCHITECTURE §1).
  - (−) Deterministic decision is more predictable than one with noise; credible
    irrationality arrives in Week 3 (memory + emotion), not here.
