# Arquitectura — Simulación Urbana Persistente (v2)

> Documento técnico de referencia. Describe **cómo** se construye lo que
> `simulacion_urbana_v2.md` define como visión y `plan_4_semanas.md` como plan.
> Para el **porqué** de cada decisión estructural, ver [DECISIONS.md](./DECISIONS.md).

---

## 1. Objetivo arquitectónico

Construir un motor de simulación social que sea, en este orden de prioridad:

1. **Determinista** — mismo `seed` ⇒ mismo run, bit a bit. Sin esto no hay forma de
   distinguir un fenómeno emergente de un bug.
2. **Auditable** — todo cambio de estado pasa por un `Event`. Siempre se puede
   responder *por qué* cambió algo.
3. **Reemplazable por capas** — cada sistema es una función pura activable por flag.
   El MVP corre con la Capa 1; el resto se enciende sin reescribir el núcleo.
4. **Heterogéneo** — los agentes difieren por rasgo (fijo) + memoria (acumula) +
   emoción (decae), no por números distintos del mismo molde.

El rendimiento **no** es un objetivo del MVP (100 agentes). Se prioriza velocidad de
iteración y claridad. La arquitectura es portable: si aparece un bottleneck, el núcleo
se reescribe sin tocar el diseño.

---

## 2. Vista de alto nivel

```text
                         ┌──────────────────────────────────────────┐
                         │                scheduler/                 │
                         │  Reloj multi-escala. Orquesta el orden.   │
                         └───────────────────┬──────────────────────┘
                                             │ por cada tick, en orden
                                             ▼
   ┌─────────────┐   lee    ┌──────────────────────────┐   emite   ┌──────────────┐
   │   state/    │ ───────▶ │         systems/         │ ────────▶ │  eventlog/   │
   │ datos puros │          │ reglas = funciones puras │  Events   │ aplica+guarda│
   │ (sin lógica)│ ◀─────── │ (estado) -> [Event]      │           │   eventos    │
   └─────────────┘  aplica  └──────────────────────────┘           └──────┬───────┘
          ▲          eventos                                               │
          └───────────────────────────────────────────────────────────────┘
                         el eventlog es el ÚNICO que muta state

   ┌─────────────┐                                   ┌──────────────────────────┐
   │ projector/  │  (Semana 4) salto offline         │        observers/        │
   │ proyección  │  determinista + estocástico       │ vistas solo-lectura (rol)│
   └─────────────┘                                   └──────────────────────────┘
```

**Invariante de flujo:** ningún `system` muta `state` directamente. Un system **lee**
estado y **devuelve** una lista de `Event`. El `eventlog` es el único componente con
permiso de escritura sobre el estado. Esto da auditoría, reproducibilidad y, más
adelante, la base para la proyección offline.

**Anillos núcleo / fachada / cliente (ADR-0011):** todo lo anterior es el **núcleo**.
A su alrededor, `facade/` expone una superficie estable (crear, avanzar, leer, guardar,
cargar) que entrega DTOs de solo lectura. Los **clientes** (una UI de escritorio hoy; un
motor gráfico mañana) hablan **solo** con la fachada; nunca importan `systems/` ni tocan
el `World`. Las dependencias apuntan hacia adentro: el núcleo no conoce a nadie de afuera.

El primer cliente es **`citysim_desktop/`** (Pygame, ADR-0012), un paquete aparte del
núcleo. Internamente se separa en *presenter* (Python puro, sin pygame, testeable sin
pantalla) y *vista* (Pygame). Pygame es dependencia opcional (`pip install ".[ui]"`).

---

## 3. Estructura de paquetes

```text
src/citysim/
├── rng.py            RNG con semilla, inyectado. Nunca se usa random global.
├── config.py         Flags de capas, parámetros del run, seed.
│
├── state/            Modelos de datos puros. Sin lógica de negocio.
│   ├── world.py          Contenedor raíz: índices de todas las entidades + reloj.
│   ├── person.py         Person: estado base + rasgos + necesidades + memoria + metas.
│   ├── household.py      Household: integrantes, ingresos, gastos, vivienda.
│   ├── place.py          Place: capacidad, horario, tipo, ubicación.
│   ├── event.py          Event: tipo, payload, tick, escala. Fuente de verdad.
│   ├── relationship.py   Relationship: tipo, fuerza, reciprocidad, historia.
│   └── enums.py          Tipos cerrados (PlaceType, EventType, RelType, TimeScale).
│
├── systems/          Las reglas. Funciones puras: (world, ctx) -> list[Event].
│   ├── base.py           Protocolo System + registro por capa/escala.
│   ├── aging.py          Envejecimiento, energía, demografía base. (Capa 1)
│   ├── needs.py          Recalcula necesidades psicológicas. (Capa 1)
│   ├── wellbeing.py      Bienestar ponderado por rasgos. (Capa 1)
│   ├── decision.py       Decisión satisficiente (no optimizadora). (Capa 1/2)
│   ├── economy.py        Trabajo, consumo, finanzas del hogar. (Capa 2)
│   ├── memory.py         Copia eventos a memoria episódica; decae. (Semana 3)
│   ├── emotion.py        Appraisal esperado-vs-real; emoción que decae. (Semana 3)
│   ├── goals.py          Formación/persecución/abandono de metas. (Semana 3)
│   ├── relations.py      Crea y actualiza vínculos. (Semana 4 / Capa 4)
│   ├── contagion.py      Difusión por la red proporcional al vínculo. (Semana 4)
│   └── death.py          Riesgo acumulado + efectos posteriores. (Semana 4)
│
├── scheduler/        El reloj.
│   └── clock.py          Escalas múltiples; orden de systems por tick.
│
├── eventlog/         El registro.
│   ├── log.py            Buffer + persistencia del historial de eventos.
│   └── apply.py          Aplicadores: cómo cada EventType muta el state.
│
├── seed/             Generación determinista de la población inicial.
│   └── seeder.py        100 personas · 30 hogares · 20 empresas · 1 barrio.
│
├── facade/           (ADR-0011) Única superficie pública para los clientes.
│   ├── simulation.py    Clase Simulation: crear/avanzar/leer/guardar/cargar.
│   └── dto.py           DTOs frozen de solo lectura (copias del estado relevante).
│
├── projector/        (Semana 4) Persistencia offline: estado proyectado.
│   └── projector.py
│
└── observers/        (Semana 4) Vistas solo-lectura según rol.
    └── citizen.py        Una sola vista para el MVP.
```

---

## 4. Modelo de datos (state/)

Modelos puros con `@dataclass`. **Sin métodos de negocio**: la lógica vive en
`systems/`. Esto los hace triviales de serializar, copiar y testear.

### Escalas de tiempo de los atributos de `Person`

La heterogeneidad nace de combinar tres escalas distintas (ver tabla en la visión):

| Concepto      | Naturaleza             | ¿Se almacena?       | Dónde vive en `Person`          |
|---------------|------------------------|---------------------|---------------------------------|
| **Rasgo**     | Estable, casi invariable | Sí, como constante  | `traits` (fijado al nacer)      |
| **Memoria**   | Acumulativa, decae lento | Sí, como registro   | `memory: list[MemoryTrace]`     |
| **Emoción**   | Transitoria, decae rápido| **Nunca fija**      | se **recalcula** cada tick      |

> Regla dura: **no se almacenan estados psicológicos arbitrarios**. "Persona triste"
> está prohibido. La emoción es una señal derivada que se recalcula; nunca un campo
> persistido. Ver `systems/emotion.py` y [DECISIONS.md → ADR-0006](./DECISIONS.md).

### Identidad de entidades

Toda entidad tiene un `id` estable (entero asignado por el seeder/RNG). Las
referencias entre entidades se hacen **por id**, nunca por puntero directo, para que
el estado sea serializable y la integridad referencial sea testeable.

---

## 5. Sistemas (systems/)

Un `System` es una función pura con la firma:

```python
def step(world: World, ctx: TickContext) -> list[Event]: ...
```

- **No muta** `world`. Lee y devuelve eventos.
- Es **determinista**: toda aleatoriedad sale de `ctx.rng`, jamás del `random` global.
- Declara su **escala** (horaria/diaria/mensual/poblacional) y su **capa** (1–6).
- Se registra en `systems/base.py`; el scheduler decide cuáles corren según la
  escala del tick actual y los flags de capa activos.

El **orden** dentro de un tick horario respeta el bucle del agente de la visión:

```text
1. aging/needs      Actualizar estado (incl. recalcular y decaer emoción).
2. emotion          Evaluación (appraisal): esperado vs real -> emoción.
3. decision         Decidir acción (satisficiente, sesgada por rasgos+emoción).
4. (ejecución)      La acción se emite como Event.
5. memory/relations Procesar eventos -> memoria episódica + red social.
6. economy/...      Hogar, economía y movilidad en su escala correspondiente.
```

---

## 6. Reloj (scheduler/)

La v1 fijaba "1 tick = 1 hora". La v2 usa **escalas múltiples**: el scheduler avanza
en ticks horarios y dispara las escalas mayores cuando corresponde.

```text
Tick horario      → conducta individual, energía, rutinas
Paso diario       → finanzas del hogar, contratos
Paso mensual      → economía agregada, mercado laboral
Paso poblacional  → demografía (nacimientos, muertes, envejecimiento)
```

En cada frontera (fin de día, fin de mes, etc.) el scheduler ejecuta los systems
registrados para esa escala, en orden de capa. Un año MVP = 365 días de ticks.

---

## 7. Eventos y eventlog (eventlog/)

- Un `Event` es un dato inmutable: `(type, tick, scale, payload)`.
- Los systems **emiten** eventos; nunca aplican cambios.
- `eventlog/apply.py` tiene un aplicador por `EventType` que sabe cómo ese evento
  muta el `world`. Es el único lugar con escritura.
- `eventlog/log.py` guarda el historial completo (fuente de verdad del run).
- **NUEVO (v2):** los eventos significativos para un agente también se copian a su
  memoria episódica (lo hace `systems/memory.py` leyendo el log del tick).

Este patrón habilita: reproducibilidad, auditoría causal, y la proyección offline
(que reconstruye/saltea estado a partir de la naturaleza de los procesos).

---

## 8. Determinismo y aleatoriedad (rng.py)

- **Un único** `random.Random(seed)` se crea en el arranque y se inyecta vía
  `TickContext`. Nada usa el `random` global.
- Para sub-streams reproducibles (p. ej. por system) se derivan generadores hijos de
  forma determinista a partir del seed maestro, no por instancias ad-hoc.
- Consecuencia: dos runs con el mismo seed producen **el mismo log de eventos**, que
  es exactamente el gate de validación de la Semana 1.

---

## 9. Persistencia offline (projector/) — Semana 4

El mayor riesgo técnico. Al reconectar **no** se simula tick a tick el tiempo
ausente: se proyecta un estado consistente separando procesos por naturaleza.

```text
Deterministas (calculables en salto):
  envejecimiento, contratos, pagos recurrentes, demografía base

Estocásticos (muestreados, no simulados tick a tick):
  accidentes, encuentros sociales, eventos de salud agudos
```

---

## 10. Tests de invariantes (la espina anti-deuda)

Propiedades que **nunca** deben romperse, chequeadas en cada run. Si una falla, se
para y se arregla: no se acumula deuda.

1. **Conservación de dinero** — no aparece ni desaparece sin un evento que lo explique.
2. **Cuadre poblacional** — vivos + muertos = nacidos. Sin fugas.
3. **Rangos válidos** — energía, bienestar, salud ∈ `[0, 1]`; edad ≥ 0.
4. **Integridad referencial** — toda relación/hogar apunta a entidades existentes.
5. **Determinismo** — dos runs con el mismo seed ⇒ logs de eventos idénticos.

Implementados en `tests/` con `pytest`. Ver [CONTEXT.md](./CONTEXT.md) para el estado
de cobertura por semana.

---

## 11. Capas activables (no fases)

Las capas son **flags**, no etapas secuenciales del código. El motor no sabe de
capas; solo activa los systems cuyo flag esté encendido.

```text
Capa 1  Personas · Hogares · Trabajo · Movilidad        ← MVP arranca aquí
Capa 2  Ingresos · Gastos · Ahorro · Comercio
Capa 3  Clima · Energía · Agua · Gas · Electricidad
Capa 4  Relaciones · Amistades · Parejas · Redes de apoyo
Capa 5  Salud física · Salud mental · Hábitos
Capa 6  Seguridad · Accidentes · Infracciones · Patrullas · Cámaras
```

---

## 12. Mapa plan → arquitectura

| Semana | Gate de validación                              | Componentes que toca                                |
|--------|-------------------------------------------------|-----------------------------------------------------|
| 1      | ¿El mundo tickea determinista y reproducible?   | `rng`, `state/*`, `eventlog`, `scheduler`, `seeder` |
| 2      | ¿Los agentes se ven distintos entre sí?         | `traits`, `needs`, `wellbeing`, `decision`, `economy` |
| 3      | ¿El pasado pesa? ¿Hay irracionalidad creíble?   | `memory`, `emotion`, `goals`                        |
| 4      | ¿La red reacciona ante una muerte/shock?        | `relations`, `contagion`, `death`, `projector`, `observers` |

---

## 13. Principios de escalabilidad (conservados)

No simular todo al máximo detalle. Niveles de abstracción:

```text
Nivel 1  Estadísticas agregadas
Nivel 2  Hogares
Nivel 3  Personas individuales
Nivel 4  Personas activas cerca del usuario
```

La complejidad sube solo cuando es necesario. No se implementa en el MVP, pero el
diseño (entidades por id, systems por capa) no lo impide.
