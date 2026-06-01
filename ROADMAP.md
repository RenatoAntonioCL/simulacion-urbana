# Roadmap

> Hacia dónde va el proyecto y cómo seguir su avance. El progreso se ve día a día en
> los **commits**, en el [CHANGELOG](./CHANGELOG.md) y en los checkboxes de abajo.
> Estado vivo y detalle técnico del momento: [CONTEXT.md](./CONTEXT.md).

El plan de construcción está en [`plan_4_semanas.md`](./plan_4_semanas.md): cada hito
cierra con un **gate** de validación (una pregunta sí/no). No se avanza con el gate sin
pasar. Cada hito mapea a una versión.

## Versionado

Mientras el MVP está en construcción, la versión vive en `0.x` y la API es inestable.
Cada hito semanal corresponde a una release alpha; el MVP cerrado (los 4 gates) marca
la primera versión estable de referencia.

| Versión        | Hito                         | Gate de validación                                   | Estado |
|----------------|------------------------------|------------------------------------------------------|--------|
| `v0.0.x`       | Núcleo determinista (Sem. 1) | ¿El mundo tickea determinista y reproducible?        | 🟡 En progreso |
| `v0.1.0-alpha` | Identidad (Sem. 2)           | ¿Los agentes se ven distintos entre sí?              | ⬜ Pendiente |
| `v0.2.0-alpha` | Trayectoria (Sem. 3)         | ¿El pasado pesa? ¿Hay irracionalidad creíble?        | ⬜ Pendiente |
| `v0.3.0-alpha` | Sociedad (Sem. 4)            | ¿La red reacciona ante una muerte / shock?           | ⬜ Pendiente |
| `v1.0.0`       | MVP cerrado                  | Los 4 gates pasados: un año reproducible y no plano  | ⬜ Pendiente |

Leyenda: ✅ hecho · 🟡 en progreso · ⬜ pendiente

---

## v0.0.x — Núcleo determinista 🟡

Motor que late: tickea de forma determinista y registra eventos. Sin comportamiento.

- [x] Arquitectura, decisiones (ADRs), contexto y changelog.
- [x] Scaffold del paquete `citysim` con contratos (state, systems, scheduler, eventlog).
- [x] RNG sembrado e inyectado; eventlog que aplica y persiste; scheduler multi-escala.
- [x] Seeder determinista (100 personas · 30 hogares · 20 empresas · 1 barrio).
- [x] Invariantes + tests (cuadre poblacional, rangos, integridad, reproducibilidad).
- [x] Dockerización (imagen multi-stage, compose, Makefile).
- [ ] Envejecimiento con demografía base completa (nacimientos/muertes por edad).
- [ ] **Gate:** dos runs con el mismo seed ⇒ mismo log; invariantes verdes tras un año.

## v0.1.0-alpha — Identidad ⬜

Que los agentes se vean distintos entre sí. Rompe la planitud.

- [ ] Rasgos en `Person` (sociabilidad, ambición, riesgo, escrupulosidad, resiliencia).
- [ ] Necesidades psicológicas (pertenencia, autonomía, propósito, seguridad, estímulo).
- [ ] Bienestar ponderado por rasgos, no solo dinero.
- [ ] Decisión satisficiente básica.
- [ ] Economía mínima (Capa 1): trabajo da ingreso, consumo gasta.
- [ ] **Gate:** dos agentes con economía similar pero rasgos opuestos deciden distinto.

## v0.2.0-alpha — Trayectoria ⬜

Que el pasado vivido cambie el presente, con irracionalidad creíble.

- [ ] Memoria episódica con decaimiento.
- [ ] Emoción transitoria por appraisal, que decae según resiliencia (nunca almacenada).
- [ ] Objetivos dinámicos (se forman, persiguen, logran o abandonan).
- [ ] Conexión memoria → decisión (un despido sube la aversión al riesgo).
- [ ] **Gate:** dos agentes iguales con historias distintas se comportan distinto hoy.

## v0.3.0-alpha — Sociedad ⬜

Que las acciones repercutan en la red y que la muerte pese.

- [ ] `Relationship` con tipo, fuerza, reciprocidad e historia.
- [ ] Contagio social por la red, proporcional a la fuerza del vínculo.
- [ ] Sistema de muerte emergente + cola de consecuencias (duelo, herencia, hogar, huella).
- [ ] Proyección offline (deterministas vs estocásticos).
- [ ] Una vista de observador (Ciudadano o Analista).
- [ ] **Gate:** una muerte bien conectada genera ondas en red y economía; shock de barrio
      produce caída de ánimo colectiva.

## v1.0.0 — MVP cerrado ⬜

Los 4 gates pasados: un año simulado, reproducible, con agentes que se ven distintos,
recuerdan, sienten, se influyen y mueren dejando huella.

---

## Después del MVP (ideas, fuera de alcance por ahora)

- Capa 2 (economía rica: ahorro, comercio, inversión) y resto de capas como flags.
- Más observadores y una UI de verdad.
- Profundizar la proyección offline para ausencias largas.
- Publicación de la imagen Docker en un registry (CI ya corre build + tests por push).
- **Firma y notarización de los ejecutables** (Apple Developer en macOS, code signing en
  Windows) para que abran sin los avisos de Gatekeeper/SmartScreen. Hoy los binarios van
  sin firmar y requieren un paso manual al abrir (ver [ADR-0013](./DECISIONS.md)).

## Cómo seguir el avance

- **Commits**: el día a día del trabajo.
- **[CHANGELOG.md](./CHANGELOG.md)**: qué cambió en cada versión.
- **[CONTEXT.md](./CONTEXT.md)**: estado vivo y próximo paso concreto.
- **Releases / tags**: cada hito alpha queda etiquetado.
