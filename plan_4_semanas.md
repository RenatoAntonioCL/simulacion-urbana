# Execution Plan — Urban Simulation MVP (4 weeks)

> Goal: go from idea to an MVP that **runs, is reproducible and is not flat**, advancing
> steadily and without technical debt. One validatable milestone per week. Do not advance
> with a broken foundation.

---

## Plan philosophy

- **Steady pace, no crunch.** The plan assumes ~2 focused work blocks per week, not a
  daily marathon. Better small and solid than large and fragile.
- **Weekly validation (gate).** Each week closes with a yes/no question. If the answer
  is "no", fix it before moving on. That is what prevents debt.
- **Agent richness is the priority.** The economy stays minimal (Layer 1 only). The
  focus is on people not being flat, which is the heart of the project.

## Recommended stack (assumed)

At MVP scale (100 people) performance is not a problem, so iteration speed is prioritized:

```text
Language      Python 3.11+
Models        dataclasses (or pydantic if validation is wanted)
Randomness    a single random.Random(seed) injected, never the global one
Tests         pytest
Persistence   JSON to start; SQLite if querying is needed
Dependencies  minimal; no heavy simulation frameworks yet
```

The architecture is portable: if a bottleneck appears later, the core can be rewritten
in another language without touching the design.

---

## The anti-debt backbone (every week)

These three practices are put in place in Week 1 and maintained throughout. They are
cheap to set up at the start and very expensive to retrofit later.

1. **Determinism with a seed.** All randomness goes through a single generator with a
   fixed `seed`. Same seed → same run. Any bug is exactly reproducible.
2. **Events as source of truth.** No system mutates state on its own: every relevant
   change is emitted as an `Event` and applied from there. This allows auditing *why*
   each thing happened and, later, the offline projection.
3. **Invariant tests.** Properties that must never be violated, checked on every run:
   - Money conservation (money does not appear or disappear without an event explaining it).
   - Population balance (alive + dead = born, no leaks).
   - Valid ranges (energy, wellbeing, health within `[0, 1]`; age ≥ 0).
   - Referential integrity (every relationship points to existing persons).

Golden rule: **if an invariant test fails, stop and fix it. Do not accumulate debt.**

---

## Base architecture

Clean separation from the start so that each system is testable and replaceable.

```text
state/        Pure data models (Person, Household, Place, Event, Relationship).
              No logic. Data only.

systems/      The rules. Pure functions: receive state, return events.
              update_persons, decide_actions, economy_step, death_system, etc.

scheduler/    The clock. Orchestrates ticks at their different scales
              (hourly, daily, monthly, population) and calls systems in order.

eventlog/     The registry. Applies events to state and saves the history.

projector/    (Week 4) Computes the projected state for offline persistence.

observers/    (Week 4) Read-only views over the state. Just one for the MVP.
```

Principle: `systems` do not mutate state directly; they **emit events** and the
`eventlog` applies them. This way the flow is always auditable.

---

# Week 1 — Deterministic core

**Goal:** a world that ticks deterministically and records events. No behavior yet:
just the skeleton that beats.

### Tasks
- Repo scaffolding, environment, `pytest`, folder structure of the base architecture.
- Data models for the entities: `Person`, `Household`, `Place`, `Event` (state only,
  no traits yet).
- Random generator with seed, injected throughout the system.
- `eventlog`: emit, apply and save events.
- `scheduler`: the tick loop with multiple scales (hourly for behavior,
  daily/monthly/population for the rest).
- Seeder: generate the initial population (100 persons, 30 households, 20 businesses,
  1 neighborhood) deterministically.
- First invariant tests (population balance, valid ranges).

### Out of scope this week
Any agent decisions. This week the world only ages and records the passage of time.

### Validation gate
> **Does the world tick deterministically and reproducibly?** Two runs with the same
> seed produce exactly the same event log. Invariants pass after simulating one year.

---

# Week 2 — Identity (traits + needs)

**Goal:** agents look distinct from each other. This is the milestone that breaks flatness.

### Tasks
- Add **traits** to `Person` (sociability, ambition, risk tolerance, conscientiousness,
  resilience), fixed at birth with population-level variation.
- Add **psychological needs** (belonging, autonomy, purpose, security, stimulation).
- Rewrite the **wellbeing** function so it depends on needs weighted by traits, not
  just money.
- Basic **satisficing decision** loop: the agent chooses the first option that is "good
  enough" according to its personal weights (still no emotion or memory).
- Minimal economy (Layer 1): work generates income, consumption spends. Just enough for
  decisions to have consequences.

### Out of scope this week
Memory, emotion, weighted relationships. Only static traits + needs + bounded decision.

### Validation gate
> **Do agents look distinct from each other?** Take two agents with similar economy but
> opposite traits and verify they make different decisions consistently (e.g.: the
> ambitious one works more hours, the sociable one prioritizes bonds). If they all
> converge to the same pattern, the weights are not working.

---

# Week 3 — Trajectory (memory + emotion + goals)

**Goal:** past lived experience changes present behavior, and credible irrationality emerges.

### Tasks
- **Episodic memory** per agent: copy significant events to the agent's memory, with
  weight that decays over time (not erased, attenuated).
- **Transient emotion**: a signal that emerges from the expected-vs-actual gap
  (appraisal), biases decisions while it lasts, and decays at a rate set by the agent's
  resilience. Never stored as fixed state: recomputed every tick.
- **Dynamic goals**: targets that form, are pursued, achieved or abandoned. Achieving
  or failing a goal moves wellbeing.
- Connect memory → decision: a past negative event biases future decisions (e.g.: a
  layoff increases risk aversion).

### Out of scope this week
Contagion and death. This week is about the individual through time.

### Validation gate
> **Does the past weigh in?** Two agents identical in traits but with different histories
> (one with a recent layoff, one without) must behave differently today. And verify that
> emotion decays: after a shock, wellbeing recovers over time at a rate consistent with
> resilience.

---

# Week 4 — Society (bonds + contagion + death) and close

**Goal:** actions have repercussions in the network, collective phenomena emerge, and
death carries weight. Close with a complete one-year run.

### Tasks
- **`Relationship`** entity with type, strength, reciprocity and history.
- **Social contagion**: moods and behaviors spread through the network, proportional to
  bond strength.
- **Complete death system**:
  - Emerges from accumulated health risk (age, habits, sustained stress, healthcare
    access) + acute events. Psychosocial factors enter as one among several, with
    restraint.
  - Downstream effects: grief in those connected (scaled by bond, decays by resilience),
    role vacancy, economic shock and inheritance, household restructuring, persistent
    trace in the memory of the living.
- **Offline projection** (`projector`): separate deterministic processes (aging,
  contracts, demographics) from stochastic ones (accidents, encounters) and project each
  with its own method on reconnection.
- **One observer view** (Citizen or Analyst) to be able to *see* what is happening.
- Validation run: simulate one full year and review the emergent phenomena.

### Out of scope this week (and from the MVP)
Layers 3 (climate/energy), 5 (detailed health) and 6 (security); remaining observers;
robust database persistence; UI beyond a basic view.

### Validation gate
> **Does the network react?** Trigger a death of a well-connected agent and verify that:
> grief propagates proportionally to bonds, the household restructures, there is an
> economic effect, and the trace persists. Also verify that after a neighborhood economic
> shock a collective mood drop emerges (contagion), not just an individual one.

---

## After the 4 weeks

If all four gates pass, you have an MVP that runs one year reproducibly, with agents
that look distinct, remember, feel, influence each other and die leaving a trace. From
there, the natural next steps (not part of this plan):

- Enable Layer 2 (richer economy: savings, commerce, investment).
- More observers and a real UI.
- Layers 3/5/6 as activatable modules.
- Deeper offline projection for long absences.

## Risks to watch

- **Premature over-engineering.** At 100 agents, optimizing wastes time. Resist the
  temptation.
- **Activating everything at once.** If you skip a gate, you will not be able to
  distinguish genuine emergence from a bug. Order matters.
- **Economy consuming the focus.** It is easy for the economic model to grow and absorb
  the time that should go toward agent richness. Keep it minimal in the MVP.
