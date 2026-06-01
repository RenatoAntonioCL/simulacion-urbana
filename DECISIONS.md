# Registro de Decisiones de Arquitectura (ADR)

> Cada decisión estructural significativa se registra aquí con su contexto y
> consecuencias. Formato ligero estilo ADR. El **qué** está en
> [ARCHITECTURE.md](./ARCHITECTURE.md); aquí vive el **porqué**.

Estados posibles: `Propuesta` · `Aceptada` · `Reemplazada por ADR-XXXX` · `Obsoleta`.

---

## ADR-0001 — Eventos como única fuente de verdad

- **Estado:** Aceptada
- **Contexto:** Si cada system muta el estado por su cuenta, es imposible auditar por
  qué cambió algo, reproducir bugs o construir la proyección offline.
- **Decisión:** Ningún system muta el estado. Los systems **emiten** `Event`; solo
  `eventlog/apply.py` aplica eventos al `World`.
- **Consecuencias:**
  - (+) Auditoría causal completa; reproducibilidad; base para la proyección offline.
  - (+) Cada cambio es testeable de forma aislada (evento → efecto esperado).
  - (−) Más verboso: todo cambio requiere definir un `EventType` y su aplicador.
  - (−) Cuidado con el orden de aplicación dentro de un tick (lo fija el scheduler).

---

## ADR-0002 — Determinismo con un único RNG sembrado e inyectado

- **Estado:** Aceptada
- **Contexto:** El proyecto necesita distinguir emergencia genuina de bug. Sin
  reproducibilidad exacta, eso es imposible.
- **Decisión:** Un único `random.Random(seed)` creado al arranque e inyectado vía
  `TickContext`. Prohibido el `random` global o instancias ad-hoc. Los sub-streams se
  derivan de forma determinista del seed maestro.
- **Consecuencias:**
  - (+) Mismo seed ⇒ mismo log de eventos, bit a bit. Bugs reproducibles.
  - (−) Disciplina permanente: cualquier `import random` suelto rompe la garantía
    (se vigila en revisión y, idealmente, con un test/lint).

---

## ADR-0003 — `state/` son datos puros; la lógica vive en `systems/`

- **Estado:** Aceptada
- **Contexto:** Mezclar datos y comportamiento en las entidades dificulta serializar,
  testear y reemplazar reglas.
- **Decisión:** Las entidades son `dataclass` sin métodos de negocio. Toda regla es
  una función pura en `systems/` con firma `(World, TickContext) -> list[Event]`.
- **Consecuencias:**
  - (+) Serialización trivial (JSON), tests simples, reglas intercambiables.
  - (+) Encaja con ADR-0001: los systems no pueden mutar porque no tienen métodos.
  - (−) Algo de fricción ergonómica (no hay `person.trabajar()`).

---

## ADR-0004 — Referencias entre entidades por `id`, no por puntero

- **Estado:** Aceptada
- **Contexto:** El estado debe ser serializable y la integridad referencial,
  testeable.
- **Decisión:** Cada entidad tiene un `id` estable. Las relaciones, hogares y lugares
  referencian a otras entidades por `id`. El `World` mantiene los índices.
- **Consecuencias:**
  - (+) Estado serializable; invariante de integridad referencial chequeable.
  - (−) Indirección: hay que resolver ids contra los índices del `World`.

---

## ADR-0005 — Capas como flags activables, no como fases de código

- **Estado:** Aceptada
- **Contexto:** La visión define 6 capas. Tratarlas como fases secuenciales obligaría
  a reescribir el motor para encender cada una.
- **Decisión:** El motor no conoce las capas. Cada system declara su capa; el
  scheduler corre solo los systems cuyo flag esté activo en `config.py`.
- **Consecuencias:**
  - (+) Se valida el MVP con Capa 1 y se enciende el resto sin tocar el núcleo.
  - (+) Permite aislar variables al depurar emergencia (encender de a una).
  - (−) Hay que mantener los flags y las dependencias entre capas coherentes.

---

## ADR-0006 — Tres escalas de estado psicológico: rasgo / memoria / emoción

- **Estado:** Aceptada
- **Contexto:** La v1 producía agentes planos y prohibía "estados psicológicos
  arbitrarios". Hay que dar profundidad sin violar esa prohibición.
- **Decisión:** Separar por escala temporal:
  - **Rasgo** — constante fijada al nacer; se almacena.
  - **Memoria** — registro acumulativo que decae lento; se almacena.
  - **Emoción** — señal transitoria derivada del appraisal; **nunca se almacena**, se
    recalcula cada tick y decae a velocidad fijada por la resiliencia.
- **Consecuencias:**
  - (+) "Persona triste" persistida sigue prohibido; la pena emerge y decae.
  - (+) Dos agentes idénticos hoy actúan distinto por su memoria distinta.
  - (−) La emoción recalculada cada tick tiene costo; aceptable a escala MVP.

---

## ADR-0007 — Decisión satisficiente, no optimización global

- **Estado:** Aceptada
- **Contexto:** Optimizadores globales perfectos se ven robóticos e idénticos.
- **Decisión:** Los agentes eligen la primera opción "suficientemente buena" según
  sus pesos personales, con información incompleta y sesgo emocional, sujeto a dinero,
  tiempo y energía.
- **Consecuencias:**
  - (+) Diversidad de conducta; la irracionalidad acotada se lee como humanidad.
  - (+) Más barato que optimizar sobre todo el espacio de acciones.
  - (−) El umbral de "suficientemente bueno" es un parámetro a calibrar.

---

## ADR-0008 — Reloj multi-escala en lugar de "1 tick = 1 hora"

- **Estado:** Aceptada
- **Contexto:** Procesos distintos (conducta vs demografía) ocurren a ritmos muy
  distintos; simular todo a escala horaria es derrochador y poco natural.
- **Decisión:** El scheduler avanza en ticks horarios y dispara escalas diaria,
  mensual y poblacional en sus fronteras, corriendo los systems de cada escala.
- **Consecuencias:**
  - (+) Eficiencia y modelado más fiel; encaja con la proyección offline.
  - (−) El orden y las fronteras entre escalas hay que mantenerlos explícitos.

---

## ADR-0009 — Stack: Python 3.11+ con dependencias mínimas, JSON primero

- **Estado:** Aceptada
- **Contexto:** A 100 agentes el rendimiento no es el problema; la velocidad de
  iteración sí. El núcleo debe ser portable si luego aparece un bottleneck.
- **Decisión:** Python 3.11+, `dataclasses`, `pytest`, RNG sembrado, persistencia en
  JSON (SQLite si se necesita consultar). Sin frameworks de simulación pesados.
- **Consecuencias:**
  - (+) Iteración rápida; barrera de entrada baja; diseño portable.
  - (−) Reescritura futura del núcleo si se escala mucho (asumido y aceptado).

---

## ADR-0010 — La muerte es un sistema emergente con cola de consecuencias

- **Estado:** Aceptada
- **Contexto:** En la v1 la muerte sería un `delete` con ajuste de ingresos: no pesa.
- **Decisión:** La muerte emerge de riesgo acumulado de salud (edad, hábitos, estrés,
  acceso a salud) + eventos agudos, con factores psicosociales como uno más entre
  varios. Dispara efectos posteriores: duelo escalado por vínculo, vacante de rol,
  shock económico + herencia, reestructuración del hogar, huella en la memoria.
- **Consecuencias:**
  - (+) Una muerte genera ondas en la red y la economía (gate de Semana 4).
  - (−) Acopla varios systems (death, relations, contagion, economy, household);
    requiere orden de aplicación cuidadoso vía eventos.
