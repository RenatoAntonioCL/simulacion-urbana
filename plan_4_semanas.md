# Plan de Ejecución — MVP Simulación Urbana (4 semanas)

> Objetivo: pasar de idea a un MVP que **corre, es reproducible y no está plano**, avanzando con constancia y sin deuda técnica. Un hito validable por semana. No se avanza con el cimiento roto.

---

## Filosofía del plan

- **Ritmo piola, no crunch.** El plan asume ~2 bloques de trabajo enfocados por semana, no una maratón diaria. Mejor poco y sólido que mucho y frágil.
- **Validación por semana (gate).** Cada semana cierra con una pregunta de sí/no. Si la respuesta es "no", se arregla antes de avanzar. Eso es lo que evita la deuda.
- **La riqueza de los agentes es la prioridad.** La economía se mantiene mínima (solo Capa 1). El foco es que la gente no sea plana, que es el corazón del proyecto.

## Stack recomendado (asumido)

A escala MVP (100 personas) el rendimiento no es problema, así que se prioriza velocidad de iteración:

```text
Lenguaje      Python 3.11+
Modelos       dataclasses (o pydantic si se quiere validación)
Aleatoriedad  un único random.Random(seed) inyectado, nunca el global
Tests         pytest
Persistencia  JSON para empezar; SQLite si se necesita consultar
Dependencias  mínimas; nada de frameworks de simulación pesados aún
```

La arquitectura es portable: si más adelante el bottleneck aparece, el núcleo se reescribe en otro lenguaje sin tocar el diseño.

---

## La espina anti-deuda técnica (todas las semanas)

Estas tres prácticas se montan en la Semana 1 y se mantienen siempre. Son baratas de poner al inicio y carísimas de retrofittear después.

1. **Determinismo con semilla.** Toda la aleatoriedad pasa por un único generador con `seed` fija. Mismo seed → mismo run. Cualquier bug se reproduce exacto.
2. **Eventos como fuente de verdad.** Ningún sistema muta el estado por su cuenta: todo cambio relevante se emite como `Event` y se aplica desde ahí. Permite auditar *por qué* pasó cada cosa y, más adelante, la proyección offline.
3. **Tests de invariantes.** Propiedades que nunca deben romperse, chequeadas en cada run:
   - Conservación de dinero (no aparece ni desaparece sin un evento que lo explique).
   - Cuadre poblacional (vivos + muertos = nacidos, sin fugas).
   - Rangos válidos (energía, bienestar, salud dentro de `[0, 1]`; edad ≥ 0).
   - Integridad referencial (toda relación apunta a personas existentes).

Regla de oro: **si un test de invariante falla, se para y se arregla. No se acumula.**

---

## Arquitectura base

Separación limpia desde el inicio para que cada sistema sea testeable y reemplazable.

```text
state/        Modelos de datos puros (Person, Household, Place, Event, Relationship).
              Sin lógica. Solo datos.

systems/      Las reglas. Funciones puras: reciben estado, devuelven eventos.
              update_persons, decide_actions, economy_step, death_system, etc.

scheduler/    El reloj. Orquesta los ticks en sus distintas escalas
              (horario, diario, mensual, poblacional) y llama a los systems en orden.

eventlog/     El registro. Aplica eventos al estado y guarda el historial.

projector/    (Semana 4) Calcula el estado proyectado para la persistencia offline.

observers/    (Semana 4) Vistas de solo-lectura sobre el estado. Una sola para el MVP.
```

Principio: los `systems` no mutan estado directamente; **emiten eventos** y el `eventlog` los aplica. Así el flujo es siempre auditable.

---

# Semana 1 — Núcleo determinista

**Meta:** un mundo que tickea de forma determinista y registra eventos. Sin comportamiento aún: solo el esqueleto que late.

### Tareas
- Scaffolding del repo, entorno, `pytest`, estructura de carpetas de la arquitectura base.
- Modelos de datos de las entidades: `Person`, `Household`, `Place`, `Event` (solo estado, sin rasgos aún).
- Generador aleatorio con semilla, inyectado en todo el sistema.
- `eventlog`: emitir, aplicar y guardar eventos.
- `scheduler`: el loop de ticks con escalas múltiples (horaria para conducta, diaria/mensual/poblacional para el resto).
- Seeder: generar la población inicial (100 personas, 30 hogares, 20 empresas, 1 barrio) de forma determinista.
- Primeros tests de invariantes (cuadre poblacional, rangos válidos).

### Fuera de alcance esta semana
Cualquier decisión de los agentes. Esta semana el mundo solo envejece y registra el paso del tiempo.

### Gate de validación
> **¿El mundo tickea de forma determinista y reproducible?** Dos runs con el mismo seed producen exactamente el mismo log de eventos. Los invariantes pasan tras simular un año.

---

# Semana 2 — Identidad (rasgos + necesidades)

**Meta:** que los agentes se vean distintos entre sí. Este es el hito que rompe la planitud.

### Tareas
- Agregar **rasgos** a `Person` (sociabilidad, ambición, tolerancia al riesgo, escrupulosidad, resiliencia), fijados al nacer con variación poblacional.
- Agregar **necesidades psicológicas** (pertenencia, autonomía, propósito, seguridad, estímulo).
- Reescribir la función de **bienestar** para que dependa de las necesidades ponderadas por los rasgos, no solo del dinero.
- Bucle de **decisión satisficiente** básico: el agente elige la primera opción "suficientemente buena" según sus pesos personales (todavía sin emoción ni memoria).
- Economía mínima (Capa 1): trabajo genera ingreso, consumo gasta. Lo justo para que las decisiones tengan consecuencia.

### Fuera de alcance esta semana
Memoria, emoción, relaciones con peso. Solo rasgos estáticos + necesidades + decisión acotada.

### Gate de validación
> **¿Los agentes se ven distintos entre sí?** Tomar dos agentes con economía similar pero rasgos opuestos y verificar que toman decisiones distintas de forma consistente (ej: el ambicioso trabaja más horas, el sociable prioriza vínculos). Si todos convergen al mismo patrón, los pesos no están funcionando.

---

# Semana 3 — Trayectoria (memoria + emoción + objetivos)

**Meta:** que el pasado vivido cambie el comportamiento presente, y que aparezca irracionalidad creíble.

### Tareas
- **Memoria episódica** por agente: copiar a su memoria los eventos significativos, con peso que decae en el tiempo (no se borra, se atenúa).
- **Emoción transitoria**: señal que emerge de la brecha esperado-vs-real (appraisal), sesga la decisión mientras dura, y decae a una velocidad que fija la resiliencia del agente. Nunca se almacena como estado fijo: se recalcula cada tick.
- **Objetivos dinámicos**: metas que se forman, persiguen, logran o abandonan. Cumplir/frustrar una meta mueve el bienestar.
- Conectar memoria → decisión: un evento negativo pasado sesga decisiones futuras (ej: un despido aumenta la aversión al riesgo).

### Fuera de alcance esta semana
Contagio y muerte. Esta semana es sobre el individuo a través del tiempo.

### Gate de validación
> **¿El pasado pesa?** Dos agentes idénticos en rasgos pero con historias distintas (uno con un despido reciente, otro sin él) deben comportarse distinto hoy. Y verificar que la emoción decae: tras un shock, el bienestar se recupera con el tiempo a ritmo coherente con la resiliencia.

---

# Semana 4 — Sociedad (vínculos + contagio + muerte) y cierre

**Meta:** que las acciones tengan repercusión en la red, que emerjan fenómenos colectivos, y que la muerte pese. Cerrar con un run completo de un año.

### Tareas
- Entidad **`Relationship`** con tipo, fuerza, reciprocidad e historia.
- **Contagio social**: estados de ánimo y conductas se difunden por la red, proporcional a la fuerza del vínculo.
- **Sistema de muerte** completo:
  - Emerge de riesgo acumulado de salud (edad, hábitos, estrés sostenido, acceso a salud) + eventos agudos. Factores psicosociales entran como uno más entre varios, con sobriedad.
  - Efectos posteriores: duelo en los conectados (escalado por vínculo, decae por resiliencia), vacante de rol, shock económico y herencia, reestructuración del hogar, huella persistente en la memoria de los vivos.
- **Proyección offline** (`projector`): separar procesos deterministas (envejecimiento, contratos, demografía) de estocásticos (accidentes, encuentros) y proyectar cada uno con su método al reconectar.
- **Una vista de observador** (la de Ciudadano o Analista) para poder *ver* lo que está pasando.
- Run de validación: simular un año completo y revisar los fenómenos emergentes.

### Fuera de alcance esta semana (y del MVP)
Capas 3 (clima/energía), 5 (salud detallada) y 6 (seguridad); el resto de observadores; persistencia en base de datos robusta; UI más allá de una vista básica.

### Gate de validación
> **¿La red reacciona?** Provocar una muerte de un agente bien conectado y verificar que: el duelo se propaga proporcional a los vínculos, el hogar se reestructura, hay efecto económico, y la huella persiste. Verificar también que tras un shock económico de barrio emerge una caída de ánimo colectiva (contagio), no solo individual.

---

## Después de las 4 semanas

Si los cuatro gates pasan, tienes un MVP que corre un año de forma reproducible, con agentes que se ven distintos, recuerdan, sienten, se influyen y mueren dejando huella. Desde ahí, los siguientes pasos naturales (no parte de este plan):

- Encender la Capa 2 (economía más rica: ahorro, comercio, inversión).
- Más observadores y una UI de verdad.
- Capas 3/5/6 como módulos activables.
- Profundizar la proyección offline para ausencias largas.

## Riesgos a vigilar

- **Sobre-ingeniería temprana.** A 100 agentes, optimizar es perder tiempo. Resistir la tentación.
- **Encender todo de golpe.** Si saltas un gate, no vas a poder distinguir emergencia genuina de un bug. El orden importa.
- **Que la economía se coma el foco.** Es fácil que el modelo económico crezca y absorba el tiempo que debería ir a la riqueza de los agentes. Mantenerla mínima en el MVP.
