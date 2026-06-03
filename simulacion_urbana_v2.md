# Persistent Urban Simulation Project — v2

## Vision

Build a persistent urban simulation where a city evolves autonomously over time, even
when the user is not connected.

The goal is not to create a traditional video game, but an artificial society capable
of generating emergent phenomena related to mobility, economy, energy, employment,
health, human relationships, safety, infrastructure, climate, commerce and culture.

The city is the protagonist. The user can observe it or participate from different
perspectives.

> **The city does not exist for the player. The player exists inside the city.**

---

# Fundamental Principle

Do not start by modeling thousands of complex variables. First define a minimal set of
rules capable of generating credible behavior. Complexity emerges progressively.

## Central Question

The simulation must answer:

> What rules produce a credible society?

Not:

> What actions can a character perform?

---

# Paradigm Shift from v1

v1 was structurally sound but produced **flat agents**. The cause was not a lack of
variables, but that all agents were the same agent: they ran the same objective function
with the same weights. They differed in their numbers, not in who they were.

v2 corrects this with four design decisions:

1. **Agents have traits.** Personality constants fixed at birth that modulate every
   decision. Same engine, different agents.
2. **Wellbeing is no longer materialistic.** Psychological needs (belonging, autonomy,
   purpose) are incorporated and weighted in wellbeing. A wealthy but isolated agent
   can be doing poorly.
3. **Agents remember.** Episodic memory creates path dependence: past lived experience
   changes present behavior.
4. **Agents satisfice, not optimize.** Bounded rationality: they choose what is "good
   enough" with incomplete information biased by emotion. Bounded irrationality reads
   as humanity.

### Resolved tension: psychological states

v1 forbade "storing arbitrary psychological states" (correct). v2 maintains that
prohibition by separating three things that live on different time scales:

| Concept | Nature | Stored? | Example |
|---|---|---|---|
| **Trait** | Stable, nearly invariant | Yes, as a constant | High resilience |
| **Memory** | Accumulative, slow decay | Yes, as a record | Layoff 2 years ago |
| **Emotion** | Transient, fast decay | Never fixed; recomputed | Grief after a loss |

Thus, a stored "sad person" remains forbidden. But `high neuroticism (trait) + recent
grief (memory) → sorrow (emergent emotion that decays) → lower wellbeing and biased
decisions` is legitimate.

---

# Fundamental Entities

## Person

Represents an individual.

### State attributes (base variables)

```text
ID
Age
Money
Time
Energy
Wellbeing
Health
Location
```

### Traits (constants, fixed at birth) — NEW

```text
Sociability         (need for connection, tolerance for isolation)
Ambition            (weight of career vs leisure)
Risk tolerance      (how uncertain decisions are evaluated)
Conscientiousness   (planning, consistency, habits)
Resilience          (speed of recovery after negative events)
```

Traits are not moods: they are parameters that modulate how the agent evaluates
everything else. They are fixed with population-level variation and partial inheritance
from progenitors.

### Psychological needs — NEW

```text
Belonging      (active social bonds)
Autonomy       (control over one's own decisions)
Purpose        (feeling useful / competent)
Security       (economic and physical stability)
Stimulation    (novelty, variety)
```

Wellbeing now depends on these needs, weighted by traits, not just on money.

### Episodic memory — NEW

```text
List of significant events experienced
Each with: type, valence, intensity, age
Decreasing weight over time (not erased, attenuated)
```

### Goals — REVISED (no longer static)

```text
Targets that form, are pursued, achieved or abandoned
Achieving or failing a goal moves wellbeing
An agent without active goals should notice it (drop in purpose)
```

---

## Household

Represents a household.

```text
Members
Income
Expenses
Dwelling
Location
```

Function: group individuals and generate family dynamics. In v2 the household also
propagates shocks (death, layoff, birth) among its members and can restructure or
dissolve.

---

## Place

Represents physical locations (homes, businesses, schools, hospitals, shops, parks).

```text
Capacity
Schedule
Location
Type
```

---

## Event

Represents any significant change in the world (birth, death, accident, layoff, hiring,
relocation, marriage, rain…).

All relevant changes are recorded as world-level events. **NEW:** significant events for
an agent are also copied to its episodic memory.

---

## Relationship — NEW ENTITY

Relationships stop being a boolean attribute and become weighted entities.

```text
Type         (family / friendship / partner / work)
Strength     (how important the bond is)
Reciprocity  (is it mutual?)
History      (shared events)
```

This is what makes a death **matter**: grief spreads through the network proportionally
to the strength of the bond.

---

# Main System Rule — REVISED

v1 said "maximize wellbeing". v2 says:

> All agents attempt to **satisfice** their wellbeing — not optimize it.

They choose the first option that is "good enough" according to their personal weights,
with incomplete information biased by the emotion of the moment, subject to constraints
of **money, time and energy**.

Perfect global optimizers look robotic and identical. Bounded rationality is what
produces behavioral diversity.

---

# Simulation Cycle — REVISED

## Multiple time scales

v1 fixed "1 tick = 1 hour" as a universal law. v2 uses different scales depending on
the process:

```text
Hourly tick        → individual behavior, energy, routines
Daily step         → household finances, contracts
Monthly step       → aggregate economy, labor market
Population step    → demographics (births, deaths, aging)
```

## During each hourly tick

1. Update person state (includes recomputing emotion and letting it decay).
2. Evaluation (appraisal): compare expected vs actual.
3. Decide action (satisfice, biased by traits + emotion).
4. Execute action on the world.
5. Process events and propagate them to memories and the social network.
6. Update households, economy and mobility at their respective scale.

---

# The Agent Loop — NEW

```text
INPUTS                  COGNITION              OUTPUT
Traits (fixed)     ┐
Needs              ├──→  Evaluation  ──→  Emotion  ──→  Decision  ──→  Action
Memory (accumulates)┘                                                     │
       ▲                                                                  ▼
       └──────────────  becomes memory  ◀──────  World + Events  ◀───────┘
```

Heterogeneity arises from combining three scales: trait (fixed), memory (accumulates),
emotion (decays). Two identical agents today act differently because they lived
different things.

---

# Fundamental Resources

## Money
Increases with work, business and investment. Decreases with consumption, transport,
housing and health.

## Time
A limited resource. Every activity consumes it.

## Energy
Physical and mental fatigue. Recovered through sleep, rest and vacation. Consumed by
work, study, commuting and stress.

## Wellbeing — REVISED
Global quality-of-life indicator. In v2 it depends on:

```text
Health
Satisfaction of psychological needs (belonging, autonomy, purpose, security, stimulation)
Relationships (quality and quantity of active bonds)
Economy
Rest
```

Weighted by the agent's traits. A sociable agent suffers more from isolation; an
ambitious one, from stagnation.

---

# Causality System — PRESERVED AND EXTENDED

Do not store arbitrary psychological states. Emotional states emerge from observable
conditions.

```text
Incorrect:  Sad person
Correct:    Unemployment + low income + family problems → ↓ wellbeing
Extended:   + high resilience → faster recovery
            + low social support → slower recovery and contagion to household
```

---

# Transient Emotion — NEW

Short-lived signals that emerge from the gap between expectation and outcome:

```text
Lost something I expected to keep   → grief
Achieved something unlikely         → euphoria
Expected help that did not arrive   → frustration
```

- Bias decisions **while they last**.
- **Decay** over time; the decay rate is set by the resilience trait.
- Never stored as fixed state: recomputed every tick.

---

# Social Contagion — NEW

Moods and behaviors spread through the relationship network, with intensity proportional
to bond strength.

This is where **collective phenomena** emerge: waves of pessimism in an economically
battered neighborhood, spreading optimism, panic, trends. It is the piece that connects
the individual with the emergent-collective dimension of the vision.

---

# Death System — NEW

In v1 death would be a `delete` with an income adjustment. In v2 it is a system with a
long tail of consequences.

## Death emerges, it is not scheduled

```text
Accumulated health risk:  age + habits + sustained stress + healthcare access
Acute events:             accidents (based on safety / mobility)
Risk factors:             prolonged isolation, chronically low wellbeing
```

> Psychosocial factors enter as **one among several** health risk factors, treated with
> restraint. A mechanical "sadness kills" is not modeled.

## Downstream effects (what makes it weigh)

```text
Grief          in those connected, scaled by bond strength,
               decays according to each person's resilience
Role vacancy   who does the work? who cares for the children?
Economic shock loss of income + inheritance
Household      restructuring or dissolution, possible relocation
Trace          the memory of the deceased keeps affecting the decisions of the living
Macro          changes the population pyramid → labor market → economy
```

Death stops being an erasure and becomes a system whose consequences propagate through
time and the network.

---

# Temporal Evolution and Offline Persistence — REVISED

The city keeps evolving even when the user closes the session. On returning, **not**
every elapsed second is simulated: a consistent projected state is computed.

```text
User leaves:   June 1, 2026
User returns:  June 10, 2026
The simulation computes the accumulated effects of those days.
```

## Projection strategy (the project's biggest technical risk)

Separate processes by nature and project each with its own method:

```text
Deterministic (computable in a jump):
  aging, contracts, recurring payments, base demographics

Stochastic (sampled, not simulated tick by tick):
  accidents, social encounters, acute health events
```

---

# Layers — REVISED (activatable modules, not phases)

Implement as flags to validate the MVP with Layer 1 active and enable the rest without
rewriting the engine.

```text
Layer 1  Persons · Households · Work · Mobility
Layer 2  Income · Expenses · Savings · Commerce
Layer 3  Climate · Energy consumption · Water · Gas · Electricity
Layer 4  Relationships · Friendships · Partners · Support networks
Layer 5  Physical health · Mental health · Habits
Layer 6  Safety · Accidents · Violations · Patrols · Cameras
```

---

# Observers

The simulation is singular; views change according to role.

```text
Citizen          Work · Family · Transport
Police           Incidents · Patrols · Alerts
Camera Operator  Events · Monitoring · Urban flows
Business         Customers · Demand · Costs
Urban Analyst    Mobility · Energy · Economy · Demographics
```

---

# Scalability Principle — PRESERVED

Do not simulate everything at maximum detail. Use levels of abstraction:

```text
Level 1  Aggregate statistics
Level 2  Households
Level 3  Individual persons
Level 4  Active persons near the user
```

Complexity only increases when necessary.

---

# Initial MVP

## Scale

```text
100 persons · 30 households · 20 businesses · 1 neighborhood
```

Goal: simulate one full year of social, economic and labor evolution.

## Recommended implementation order — NEW

The risk of adding everything at once is being unable to distinguish genuine emergence
from a bug. Enable in stages and validate between each one:

```text
1. Base engine + traits + non-economic needs
   → Validate: do agents look distinct from each other?
2. Episodic memory + dynamic goals
   → Validate: does the past change the present?
3. Transient emotion + satisficing decision
   → Validate: is there credible irrationality?
4. Weighted relationships + social contagion
   → Validate: do collective phenomena emerge?
5. Complete death system
   → Validate: does a death generate ripples in the network and economy?
```

---

# Final Goal

Build a persistent city where people are born, work, study, form relationships, consume
resources, age, **remember, feel, decide with bias**, influence others, shape the
economy, transform neighborhoods, generate collective phenomena and die leaving a trace.

All from simple, consistent rules.

> The city does not exist for the player. The player exists inside the city.
