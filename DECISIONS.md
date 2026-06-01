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

## ADR-0011 — Arquitectura núcleo / fachada / cliente

- **Estado:** Aceptada
- **Contexto:** El proyecto deja de ser solo un motor que escupe un log y pasa a ser
  una **aplicación de escritorio descargable** (Windows, macOS, Linux) donde cada
  usuario crea y observa sus propios mundos. El horizonte incluye conectar a futuro un
  motor gráfico (Godot/Unity). Si el núcleo de simulación y la capa visual quedan
  acoplados, agregar o cambiar la interfaz obligaría a reescribir el motor. Hay que
  garantizar que la interfaz sea una pieza intercambiable, no una dependencia del
  núcleo.
- **Decisión:** Tres anillos con dependencias en una sola dirección (de afuera hacia
  adentro; el núcleo no conoce a nadie de afuera):
  1. **Núcleo** (`citysim/` actual: `state`, `systems`, `eventlog`, `scheduler`,
     `seed`, `invariants`, `rng`). No cambia. Su responsabilidad es avanzar la
     simulación y custodiar el estado. No sabe nada de UI, ventanas ni renderizado.
  2. **Fachada** (`citysim/facade/`): una interfaz estable y mínima — la **única**
     superficie que los clientes pueden tocar. Expone operaciones de alto nivel (crear
     mundo, avanzar, leer estado, leer eventos, guardar, cargar) y entrega **DTOs de
     solo lectura**, nunca las entidades internas del `World`. Es el contrato que
     desacopla núcleo y clientes.
  3. **Clientes** (fuera del paquete núcleo): consumen solo la fachada. Hoy, una UI de
     escritorio. Mañana, Godot/Unity u otros. Ninguno importa de `systems/`,
     `eventlog/` ni toca el `World` directamente.
- **Consecuencias:**
  - (+) La UI es reemplazable sin tocar el motor; un motor gráfico futuro se conecta a
    la misma fachada (es, de hecho, el puente hacia Godot/Unity).
  - (+) La fachada es un punto natural para serializar mundos: como el núcleo es
    determinista y sembrado (ADR-0002), un mundo se define por `config + seed`, así que
    guardar/compartir un mundo es guardar/compartir poco. El guardado se implementa por
    *replay* (`config + ticks`), evitando serializar punteros (ADR-0004).
  - (+) Los DTOs de solo lectura impiden que un cliente corrompa el estado por
    accidente, preservando ADR-0001 (eventos como única vía de cambio).
  - (+) Testeable: la fachada se puede ejercitar sin ninguna UI montada.
  - (−) Capa extra de mapeo (entidad interna → DTO) con algo de duplicación y costo de
    mantenimiento cuando el estado cambie de forma.
  - (−) Disciplina permanente: la regla "los clientes solo hablan con la fachada" hay
    que vigilarla en revisión; un import directo a `systems/` desde un cliente la
    rompe.
  - (−) La fachada debe permanecer estable; cambiarla rompe a todos los clientes a la
    vez, así que sus cambios se piensan con más cuidado que los internos.

## ADR-0012 — Primer cliente visual: Pygame in-process, separado en presenter/vista

- **Estado:** Aceptada
- **Contexto:** Con la fachada lista (ADR-0011) toca la primera interfaz visual. El
  objetivo es una aplicación de escritorio descargable y multiplataforma, con horizonte
  a un motor gráfico (Godot/Unity). Hay que elegir herramienta para el primer cliente y
  una estructura interna que no se vuelva un callejón sin salida. Las librerías de
  formularios (Tkinter/Qt) sirven para paneles, no para dibujar un barrio con cosas
  moviéndose; chocan con ese horizonte. Saltar ya a Godot agrega un puente IPC y un
  segundo lenguaje antes de ver algo en pantalla.
- **Decisión:** El primer cliente es **Pygame, in-process**, en un paquete separado del
  núcleo, `citysim_desktop/`, que consume **solo** `citysim.facade` y `citysim.config`.
  Internamente se parte en dos:
  1. **Presenter** (`controller.py`, `layout.py`): Python puro, **sin pygame**. Maneja
     la `Simulation`, traduce intenciones de UI a llamadas a la fachada y deriva la
     disposición visual desde los ids (el núcleo no tiene coordenadas — ADR-0004).
  2. **Vista** (`view.py`): Pygame. Solo dibuja lo que el presenter expone y envía input.
  Pygame entra como **dependencia opcional** (`pip install ".[ui]"`); el núcleo y la
  fachada siguen sin dependencias (ADR-0009).
- **Consecuencias:**
  - (+) Mínima fricción para validar la fachada con algo visible y empaquetable a
    ejecutable (PyInstaller) en los tres SO.
  - (+) El presenter, sin pygame, se testea sin display (corre en CI sin pantalla); la
    vista queda como pieza reemplazable. El día de Godot/Unity, se cambia la vista y el
    presenter/fachada siguen igual — es el mismo límite de ADR-0011, un nivel más arriba.
  - (+) El núcleo no gana dependencias: `import citysim.facade` funciona sin pygame.
  - (−) Pygame tiene techo gráfico bajo; no es un motor. El salto a Godot/Unity sigue
    siendo trabajo aparte (su puente es la fachada).
  - (−) Disciplina extra: hay que vigilar que la vista no filtre lógica de simulación y
    que el cliente no importe del núcleo más allá de la fachada (cubierto por un test).

## ADR-0013 — Empaquetado a ejecutable con PyInstaller, build por-SO en CI

- **Estado:** Aceptada
- **Contexto:** El objetivo del cliente (ADR-0012) es ser una app de escritorio
  **descargable** para Windows, macOS y Linux, sin pedirle al usuario que instale Python.
  Empaquetar Pygame con PyInstaller tiene tropezones conocidos: las fuentes del sistema
  pueden no estar en el binario congelado, el directorio de trabajo no es confiable al
  lanzar con doble clic, y PyInstaller **no** cross-compila.
- **Decisión:** Empaquetar con **PyInstaller** en modo **onefile** (un solo archivo
  descargable), con un `.spec` versionado (`packaging/citysim-desktop.spec`) y un script
  de entrada fino (`packaging/entry.py`). Para esquivar los tropezones:
  - **Fuente:** la vista usa la **fuente integrada de Pygame**
    (`pygame.font.Font(None, …)`), que viaja con Pygame; no se bundlean `.ttf` ni se usa
    `SysFont`. Elimina la dependencia de fuentes del SO sin `--add-data`.
  - **Guardado:** los mundos se guardan en un **directorio de datos del usuario** por SO
    (`citysim_desktop/paths.py`), no junto al binario ni en el cwd.
  - **Build por-SO:** un workflow `package.yml` con matriz
    `ubuntu`/`windows`/`macos` construye un binario por plataforma (PyInstaller no
    cross-compila). Cada job valida el binario con un modo **`--smoke`** headless
    (`SDL_VIDEODRIVER=dummy`) que crea un mundo, avanza y sale 0; luego lo sube como
    artifact. En tags `vX.Y.Z`, además lo adjunta a un GitHub Release.
  - **Disparo:** solo `workflow_dispatch` y tags `v*` (no en cada PR, para no quemar
    minutos). PyInstaller entra como extra opcional `build`; el núcleo sigue sin
    dependencias (ADR-0009).
- **Consecuencias:**
  - (+) Ejecutables descargables para los tres SO, sin que el usuario instale nada.
  - (+) El modo `--smoke` da una señal real de que el bundle arranca en cada SO, sin
    necesidad de pantalla en CI.
  - (+) Núcleo y fachada intactos y sin dependencias nuevas; todo el cambio vive en el
    cliente y en `packaging/`.
  - (−) Tres builds separados (uno por SO); no hay un único artefacto universal.
  - (−) Los binarios no están firmados: macOS/Windows pueden advertir al abrirlos
    (Gatekeeper/SmartScreen). Firmar/notarizar queda fuera de alcance por ahora.
  - (−) onefile arranca algo más lento (se autoextrae); si diera problemas en algún SO,
    el fallback documentado en el `.spec` es pasar a onedir.

## ADR-0014 — Identidad (Semana 2): decisión determinista, acción como estado, dinero conservado

- **Estado:** Aceptada
- **Contexto:** La Semana 2 da heterogeneidad a los agentes (rasgos + necesidades +
  bienestar + decisión + economía mínima). Hubo que resolver tres cosas: de dónde sale la
  diversidad de decisiones, cómo conectar "decidir" con "tener consecuencia económica" sin
  acoplar systems, y cómo evitar que el dinero se cree o destruya.
- **Decisión:**
  1. **Decisión determinista, no estocástica.** El system `decision` elige la primera
     acción "suficientemente buena" (ADR-0007) puntuada por rasgos+necesidades, sin
     `ctx.rng`. La diversidad nace de los **rasgos**, que el seeder muestrea con variación
     poblacional del RNG sembrado (ADR-0002). Consecuencia buscada: el log ahora **diverge
     por seed** (rasgos distintos ⇒ decisiones distintas), reforzando el determinismo de
     punta a punta sin azar por tick.
  2. **Economía mínima en `L1_BASE`** (como dice el plan). Corre en el MVP por defecto;
     `L2_ECONOMY` se reserva para la economía rica (ahorro/comercio/inversión) del post-MVP.
  3. **`Person.current_action`** como *estado de actividad* (no emoción — ADR-0006 prohíbe
     persistir ánimo, no la actividad en curso, igual que `location_id`). `decision` la fija
     vía el evento `ACTION_CHOSEN`; `economy` la lee para emitir `INCOME`/`EXPENSE`. Así
     decisión y economía quedan desacopladas: se comunican por estado + eventos, no por
     llamadas.
  4. **Conservación de dinero** como invariante (#1 de ARCHITECTURE §10): el total actual
     debe cuadrar con el inicial sembrado más Σ`INCOME` − Σ`EXPENSE`. El gasto se limita a
     lo disponible (`min(costo, dinero)`) para que el cuadre sea exacto.
- **Consecuencias:**
  - (+) Gate de la Semana 2 verificable: rasgos opuestos ⇒ decisiones distintas y estables.
  - (+) Determinismo más fuerte y testeable (seeds distintos ⇒ logs distintos).
  - (+) La economía no puede "fabricar" dinero sin que un invariante lo detecte.
  - (−) `decision`/`needs`/`wellbeing` emiten muchos eventos (por persona y tick); se
    mitiga emitiendo needs/wellbeing solo ante cambios ≥ ε, pero el log de un año es grande
    (perf no es objetivo del MVP — ARCHITECTURE §1).
  - (−) La decisión determinista es más predecible que una con ruido; la irracionalidad
    creíble llega en la Semana 3 (memoria + emoción), no aquí.
