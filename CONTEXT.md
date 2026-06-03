# Contexto del Proyecto

> Estado vivo del proyecto: dónde estamos, qué sigue y cómo trabajar acá.
> Se actualiza al cerrar cada semana/hito. Última actualización: **2026-06-02**.

---

## Qué es esto

Una **simulación urbana persistente**: una ciudad que evoluciona de forma autónoma en
el tiempo, incluso con el usuario desconectado. El objetivo no es un videojuego sino
una **sociedad artificial** que genere fenómenos emergentes (movilidad, economía,
relaciones, salud, muerte). La ciudad es el protagonista.

> La ciudad no existe para el jugador. El jugador existe dentro de la ciudad.

Documentos de origen:
- **`simulacion_urbana_v2.md`** — visión y modelo conceptual (el *qué* y el *porqué*).
- **`plan_4_semanas.md`** — plan de ejecución del MVP con gates semanales.
- **`ARCHITECTURE.md`** — cómo se construye técnicamente.
- **`DECISIONS.md`** — decisiones de arquitectura (ADRs) con su justificación.
- **`CHANGELOG.md`** — qué cambió y cuándo.

---

## Estado actual

| Aspecto            | Estado                                                        |
|--------------------|--------------------------------------------------------------|
| Fase               | **Semana 3 — Trayectoria** (memoria + emoción + objetivos)   |
| Semana 1 (Núcleo)  | 🟡 En progreso: motor late, tickea y registra eventos        |
| Semana 2 (Identidad)| ✅ Rasgos, needs, wellbeing, decisión, economía (v0.2.0-alpha) |
| Semana 3 (Trayectoria)| ✅ Memoria episódica, emoción transitoria, metas dinámicas (v0.3.0-alpha) |
| Semana 4 (Sociedad)| ⬜ Pendiente                                                 |
| Plataforma         | ✅ Fachada + cliente Pygame + ejecutables (release v0.1.0)   |
| Capas activas      | Capa 1 (Personas · Hogares · Trabajo · Movilidad · economía mínima) |
| Tests              | ✅ 49 tests verdes (invariantes, reproducibilidad, fachada, UI, gates Sem. 2 y 3) |

Leyenda: ✅ hecho · 🟡 en progreso · ⏳ siguiente · ⬜ pendiente

### Lo que existe y FUNCIONA hoy
- Documentación de arquitectura, decisiones, contexto y changelog.
- Paquete `src/citysim/` con el contrato completo (state, systems, scheduler, eventlog,
  seed, projector, observers).
- **Núcleo determinista que corre**: `python -m citysim --days 30` siembra 100
  personas · 30 hogares · 50 lugares, tickea un mes y registra ~3.7k eventos.
- RNG sembrado e inyectado; eventlog que aplica y persiste; scheduler multi-escala;
  seeder determinista; system `aging` de ejemplo.
- `invariants.py` + `tests/` (7 tests verdes): cuadre poblacional, rangos válidos,
  integridad referencial y reproducibilidad por seed.
- **Dockerización completa**: `Dockerfile` multi-stage (build/test/runtime no-root),
  `docker-compose.yml`, `Makefile` y `.dockerignore`. `make build/run/test` funcionan;
  el run en contenedor reproduce la misma huella de log que el local.

### Lo que es STUB todavía (NotImplementedError consciente)
- Systems de Semana 4: `relations`, `contagion`, `death`.
- Proyección offline (`projector`) y observadores (Semana 4).

> Nota sobre determinismo: con solo `aging` (seed-independiente), el log de eventos aún
> no diverge entre seeds; la semilla hoy solo afecta la población inicial. La
> divergencia del log por seed llegará con los systems estocásticos. El test lo
> documenta y deberá fortalecerse entonces.

---

## Próximo paso concreto

Arrancar la **Semana 4 — Sociedad** (relaciones, contagio, muerte):
1. Entidad `Relationship` con tipo, fuerza, reciprocidad e historia.
2. Contagio social: estados de ánimo se difunden por la red (proporcional a fuerza del vínculo).
3. Sistema de muerte emergente + cola de consecuencias (duelo, herencia, reestructuración de hogar).
4. Proyección offline (`projector`) y una vista de observador.

**Gate de Semana 4:** una muerte bien conectada genera ondas en red y economía;
shock de barrio produce caída de ánimo colectiva.

---

## Escala del MVP

```text
100 personas · 30 hogares · 20 empresas · 1 barrio · 1 año simulado
```

---

## Cómo trabajar acá (convenciones)

- **Determinismo primero.** Toda aleatoriedad pasa por el RNG inyectado. Nunca el
  `random` global. (ADR-0002)
- **Eventos para todo cambio.** Los systems no mutan estado; emiten `Event`. Solo el
  `eventlog` aplica. (ADR-0001)
- **`state/` es solo datos.** La lógica va en `systems/`. (ADR-0003)
- **No avanzar con el cimiento roto.** Si un test de invariante falla, se para y se
  arregla. No se acumula deuda.
- **No encender capas de golpe.** Se valida de a una para poder distinguir emergencia
  de bug. (ADR-0005)
- **La riqueza de los agentes es la prioridad.** La economía se mantiene mínima en el
  MVP; que no se coma el foco.

## Idioma
- Documentación y comentarios: **español**.
- Identificadores de código: **inglés** (`Person`, `Household`, `decide_action`).

---

## Riesgos vigentes

- **Proyección offline** — el mayor riesgo técnico; se aborda en Semana 4.
- **Sobre-ingeniería temprana** — a 100 agentes, optimizar es perder tiempo.
- **Economía absorbente** — tiende a crecer y robar foco; mantenerla mínima.
- **Saltar un gate** — sin validar cada hito no se distingue emergencia de bug.
