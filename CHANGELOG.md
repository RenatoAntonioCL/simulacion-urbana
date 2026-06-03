# Changelog

Todos los cambios notables del proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto adopta [Versionado Semántico](https://semver.org/lang/es/). Mientras el MVP
esté en desarrollo, la versión se mantiene en `0.x` y la API se considera inestable.

## [No publicado]

## [0.3.0-alpha] — 2026-06-02

Hito **Trayectoria** (Semana 3): el pasado vivido cambia el comportamiento presente.
Gate pasado: dos agentes idénticos en rasgos pero con historias distintas deciden
distinto hoy; la emoción decae a un ritmo coherente con la resiliencia.
La versión empaquetada es `0.3.0a1` (PEP 440); el tag del hito es `v0.3.0-alpha`.

### Added
- **Semana 3 — Trayectoria**: el pasado pesa.
  - **`systems/memory.py`** (escala diaria): envejece trazas episódicas (`age_ticks += 1`)
    y registra estados significativos (bienestar bajo, desempleo con propósito caído).
    Emite `MEMORY_UPDATED`; el aplicador reconstruye `Person.memory` desde el payload.
  - **`systems/emotion.py`**: función pura `compute(person) → float [-1, 1]`. Señal
    emocional transitoria calculada como suma ponderada de valences con decaimiento
    exponencial (sin normalizar) — un recuerdo muy antiguo pierde peso absoluto y el
    ánimo converge a 0. Resiliencia alta → tasa de decaimiento mayor → recuperación más
    rápida. Nunca almacenada; recalculada cada tick en `decision.py`.
  - **`systems/goals.py`** (escala diaria): metas dinámicas `earn_more` y `find_work`.
    Se forman cuando la necesidad y el rasgo lo indican; se logran cuando la condición
    se cumple. Un logro deja traza positiva en memoria; un abandono, negativa.
  - **`systems/decision.py`**: `_scores()` incorpora la señal emocional como modificador
    aditivo (±0.10 × mood) en `work`, `rest` y `consume`. Un agente con recuerdo de
    desempleo reciente reduce su puntaje de `work` y eleva el de `rest`, pudiendo cruzar
    el umbral de decisión satisficiente hacia la inacción.
  - `EventType.MEMORY_UPDATED` añadido al enum de tipos cerrados.
  - Aplicadores en `eventlog/apply.py` para `MEMORY_UPDATED`, `GOAL_FORMED`,
    `GOAL_ACHIEVED` y `GOAL_ABANDONED`.
- **Corrección del workflow `package.yml`**: `prerelease: ${{ contains(github.ref, '-') }}`
  para marcar automáticamente los tags con guión (alpha/beta/rc) sin intervención manual.
- 8 tests nuevos (`test_week3_trajectory.py`): señal emocional sin memoria, con memoria
  negativa/positiva, decaimiento con el tiempo, efecto de resiliencia, y el gate central
  (mismos rasgos + distinta historia → distinta acción). **49 tests verdes en total.**

## [0.2.0-alpha] — 2026-06-01

Hito **Identidad** (Semana 2): los agentes dejan de ser planos — rasgos, necesidades,
bienestar dependiente de ellos, decisión satisficiente y economía mínima. Gate pasado.
La versión empaquetada es `0.2.0a1` (PEP 440); el tag del hito es `v0.2.0-alpha`.

### Added
- **Semana 2 — Identidad** (ADR-0014): los agentes dejan de ser planos.
  - **Rasgos** en `Person`, sembrados con variación poblacional (sociabilidad, ambición,
    tolerancia al riesgo, escrupulosidad, resiliencia).
  - Systems nuevos (Capa 1, escala horaria): `needs` (recalcula necesidades), `wellbeing`
    (bienestar ponderado por rasgos, no solo dinero), `decision` (satisficiente,
    determinista, ADR-0007) y `economy` (trabajo da ingreso, consumo gasta).
  - `Person.current_action` como estado de actividad; el seeder emplea a personas en edad
    laboral.
  - **Invariante de conservación de dinero** (ARCHITECTURE §10 #1) + rangos [0,1] para
    rasgos/necesidades. Determinismo reforzado: seeds distintos ⇒ logs distintos.
  - Fachada: `PersonDTO` expone `traits`, `needs` y `current_action` (aditivo).
  - Gate verificado por test: dos agentes con economía similar y rasgos opuestos deciden
    distinto de forma consistente (ambicioso → trabajar, sociable → socializar).

## [0.1.0] — 2026-06-01

Primer hito con **aplicación de escritorio descargable**: núcleo + fachada + cliente
Pygame + empaquetado a ejecutables (Win/Mac/Linux).

### Added
- **Empaquetado a ejecutable** (PyInstaller, ADR-0013): el cliente se empaqueta a
  ejecutables nativos (onefile) para Windows, macOS y Linux. `packaging/` contiene el
  `.spec` versionado y el script de entrada; un nuevo workflow `package.yml` construye un
  binario por SO en matriz, lo valida con un modo `--smoke` headless y lo sube como
  artifact (y lo adjunta a un Release en tags `v*`). Pygame usa su fuente integrada (no
  depende de fuentes del SO) y los mundos se guardan en un directorio de datos del usuario
  (`citysim_desktop/paths.py`). PyInstaller es extra opcional `[build]`; el núcleo sigue
  sin dependencias.
- **Cliente de escritorio** (`citysim_desktop/`, ADR-0012): primera interfaz visual en
  Pygame, conectada solo a la fachada. Pantalla de creación de mundo (seed, personas,
  hogares, empresas), vista del barrio (lugares + personas con disposición determinista
  por id), feed de eventos, controles de reloj (play/pausa, velocidad, paso) y
  guardar/cargar. Separado en **presenter** (`controller.py`/`layout.py`, Python puro,
  testeable sin pantalla) y **vista** (`view.py`, Pygame). Pygame es dependencia
  **opcional** (`pip install ".[ui]"`); el núcleo sigue sin dependencias. Se ejecuta con
  `python -m citysim_desktop`. 10 tests nuevos del presenter/layout (sin display).
- **Capa de fachada** (`citysim/facade/`, ADR-0011): clase `Simulation` como única
  superficie pública para futuros clientes (UI de escritorio, motor gráfico). Expone
  crear mundo, avanzar (`advance`/`advance_days`), leer estado y eventos recientes,
  `check_invariants`, y `save`/`load`. Entrega **DTOs de solo lectura** (`PersonDTO`,
  `HouseholdDTO`, `PlaceDTO`, `RelationshipDTO`, `EventDTO`, `WorldStateDTO`); nunca las
  entidades internas del `World`. El núcleo no se tocó. Guardado por *replay*
  (`config + ticks`), exacto gracias al determinismo (ADR-0002) y sin serializar
  punteros (ADR-0004).
- **Integración continua (GitHub Actions)**: workflow `ci.yml` que en cada push/PR a
  `main` corre la suite en Python 3.11 y 3.12 y, en paralelo, construye la imagen Docker
  (stages `test` y `runtime`) con un smoke run. Badge de estado en el README.
- **Dockerización del proyecto** (orientado a portafolio):
  - `Dockerfile` multi-stage (`builder` / `test` / `runtime`): instala en venv aislado,
    corre la suite en el stage `test` e imagen final mínima (~220 MB) con usuario
    no-root `sim` y labels OCI.
  - `docker-compose.yml` con servicios `sim` (ejecución, volumen `./runs`) y `tests`.
  - `Makefile` con atajos: `build`, `run`, `test`, `shell`, `clean`, `help`.
  - `.dockerignore`.
  - README: sección "Puesta en marcha con Docker" como vía recomendada.

### Verificado
- `docker build --target test` → 7 tests verdes dentro del contenedor.
- `docker run --rm citysim --days 30` reproduce la misma huella de log que el run local
  (`4c2ff62fcf8a4d38…`): el determinismo se sostiene entre entornos.
- `docker compose config` válido; `compose run sim/tests` funcionan.

### Por hacer (completar Semana 1 / abrir Semana 2)
- Reforzar el gate de determinismo cuando entren systems estocásticos.
- Semana 2: rasgos + necesidades en `Person`/seeder, `wellbeing`, decisión satisficiente.

---

## [0.0.1] — 2026-06-01

### Added
- Documentación de arquitectura del proyecto:
  - `ARCHITECTURE.md` — vista de alto nivel, estructura de paquetes, flujo de eventos,
    determinismo, reloj multi-escala, capas activables y mapa plan→arquitectura.
  - `DECISIONS.md` — 10 ADRs iniciales (eventos como fuente de verdad, determinismo,
    state puro, referencias por id, capas como flags, tres escalas psicológicas,
    decisión satisficiente, reloj multi-escala, stack, muerte emergente).
  - `CONTEXT.md` — estado vivo del proyecto, próximos pasos y convenciones.
  - `CHANGELOG.md` — este archivo. `README.md`.
- Paquete `src/citysim/` siguiendo la arquitectura base del plan: `state/`, `systems/`,
  `scheduler/`, `eventlog/`, `seed/`, `projector/`, `observers/`, con contratos
  (protocolos, firmas) y `enums` de tipos cerrados.
- **Núcleo determinista funcional (esqueleto de Semana 1):**
  - `rng.py` — RNG sembrado e inyectado, con derivación de sub-streams.
  - `state/` — modelos puros: `World`, `Person` (estado base + huecos de rasgos/
    necesidades/memoria/metas), `Household`, `Place`, `Relationship`, `Event`.
  - `eventlog/` — emite, aplica (un aplicador por `EventType`) y persiste eventos;
    único componente con escritura sobre el estado.
  - `scheduler/clock.py` — reloj multi-escala (horaria/diaria/mensual/poblacional) con
    registro de systems filtrado por capa y ordenado.
  - `seed/seeder.py` — población inicial determinista (100·30·20·1).
  - `systems/aging.py` — primer system de ejemplo (envejecimiento).
  - `invariants.py` — cuadre poblacional, rangos válidos, integridad referencial.
  - `__main__.py` — `python -m citysim` corre un run y reporta invariantes.
- `tests/` con `pytest`: 7 tests verdes (invariantes tras un run + reproducibilidad).
- Stubs con `NotImplementedError` consciente para los systems de Semanas 2-4, el
  `projector` y el observador Ciudadano.

### Verificado
- `python -m citysim --days 30` corre limpio: 100 personas, 50 lugares, ~3720 eventos.
- Los 7 tests pasan. Invariantes verdes en estado inicial y tras simular.

### Notas
- Punto de partida: los documentos de visión (`simulacion_urbana_v2.md`) y plan
  (`plan_4_semanas.md`) ya existían. Esta versión añade la arquitectura técnica y un
  esqueleto de motor que ya tickea de forma determinista; el **comportamiento** de los
  agentes (decisión, emoción, memoria, sociedad) todavía es stub.
