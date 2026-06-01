# Proyecto de Simulación Urbana Persistente — v2

## Visión

Construir una simulación urbana persistente donde una ciudad evoluciona de forma autónoma a través del tiempo, incluso cuando el usuario no está conectado.

El objetivo no es crear un videojuego tradicional, sino una sociedad artificial capaz de generar fenómenos emergentes relacionados con movilidad, economía, energía, empleo, salud, relaciones humanas, seguridad, infraestructura, clima, comercio y cultura.

La ciudad es el protagonista. El usuario puede observarla o participar desde distintas perspectivas.

> **La ciudad no existe para el jugador. El jugador existe dentro de la ciudad.**

---

# Principio Fundamental

No se debe comenzar modelando miles de variables complejas. Primero se define un conjunto mínimo de reglas capaces de generar comportamientos creíbles. La complejidad emerge progresivamente.

## Pregunta Central

La simulación debe responder:

> ¿Qué reglas producen una sociedad creíble?

No:

> ¿Qué acciones puede realizar un personaje?

---

# Cambio de Paradigma respecto a la v1

La v1 era estructuralmente sólida pero producía **agentes planos**. La causa no era falta de variables, sino que todos los agentes eran el mismo agente: corrían la misma función objetivo con los mismos pesos. Diferían en sus números, no en quiénes eran.

La v2 corrige esto con cuatro decisiones de diseño:

1. **Los agentes tienen rasgos.** Constantes de personalidad fijadas al nacer que modulan toda decisión. Mismo motor, agentes distintos.
2. **El bienestar deja de ser materialista.** Se incorporan necesidades psicológicas (pertenencia, autonomía, propósito) que el bienestar pondera. Un agente rico pero aislado puede estar mal.
3. **Los agentes recuerdan.** Memoria episódica que crea dependencia de trayectoria: el pasado vivido cambia el comportamiento presente.
4. **Los agentes satisfacen, no optimizan.** Racionalidad acotada: eligen lo "suficientemente bueno" con información incompleta y sesgada por emoción. La irracionalidad acotada se lee como humanidad.

### Tensión resuelta: estados psicológicos

La v1 prohibía "almacenar estados psicológicos arbitrarios" (correcto). La v2 mantiene esa prohibición separando tres cosas que viven en escalas de tiempo distintas:

| Concepto | Naturaleza | ¿Se almacena? | Ejemplo |
|---|---|---|---|
| **Rasgo** | Estable, casi invariable | Sí, como constante | Alta resiliencia |
| **Memoria** | Acumulativa, decae lento | Sí, como registro | Despido hace 2 años |
| **Emoción** | Transitoria, decae rápido | Nunca fija; se recalcula | Pena tras una pérdida |

Así, "Persona triste" almacenada sigue prohibido. Pero `alto neuroticismo (rasgo) + duelo reciente (memoria) → pena (emoción emergente que decae) → menos bienestar y decisiones sesgadas` es legítimo.

---

# Entidades Fundamentales

## Person

Representa un individuo.

### Atributos de estado (variables base)

```text
ID
Edad
Dinero
Tiempo
Energía
Bienestar
Salud
Ubicación
```

### Rasgos (constantes, fijados al nacer) — NUEVO

```text
Sociabilidad        (necesidad de vínculo, tolerancia al aislamiento)
Ambición            (peso de carrera vs ocio)
Tolerancia al riesgo (cómo evalúa decisiones inciertas)
Escrupulosidad      (planificación, constancia, hábitos)
Resiliencia         (velocidad de recuperación tras eventos negativos)
```

Los rasgos no son estados de ánimo: son parámetros que modulan cómo el agente evalúa todo lo demás. Se fijan con variación poblacional y herencia parcial de los progenitores.

### Necesidades psicológicas — NUEVO

```text
Pertenencia    (vínculos sociales activos)
Autonomía      (control sobre las propias decisiones)
Propósito      (sentirse útil / competente)
Seguridad      (estabilidad económica y física)
Estímulo       (novedad, variedad)
```

El bienestar pasa a depender de estas necesidades, ponderadas según los rasgos, no solo del dinero.

### Memoria episódica — NUEVO

```text
Lista de eventos significativos vividos
Cada uno con: tipo, valencia, intensidad, antigüedad
Peso decreciente con el tiempo (no se borra, se atenúa)
```

### Objetivos — REVISADO (ya no estático)

```text
Metas que se forman, se persiguen, se logran o se abandonan
Cumplir o frustrar una meta mueve el bienestar
Un agente sin metas activas debería notarlo (caída de propósito)
```

---

## Household

Representa un hogar.

```text
Integrantes
Ingresos
Gastos
Vivienda
Ubicación
```

Función: agrupar individuos y generar dinámicas familiares. En la v2 el hogar también propaga shocks (muerte, despido, nacimiento) entre sus integrantes y puede reestructurarse o disolverse.

---

## Place

Representa lugares físicos (casas, empresas, escuelas, hospitales, comercios, parques).

```text
Capacidad
Horario
Ubicación
Tipo
```

---

## Event

Representa cualquier cambio significativo en el mundo (nacimiento, muerte, accidente, despido, contratación, mudanza, matrimonio, lluvia…).

Todos los cambios relevantes se registran como eventos a nivel mundo. **NUEVO:** los eventos significativos para un agente también se copian a su memoria episódica.

---

## Relationship — NUEVA ENTIDAD

Las relaciones dejan de ser un atributo booleano y pasan a ser entidades con peso.

```text
Tipo         (familia / amistad / pareja / laboral)
Fuerza       (qué tan importante es el vínculo)
Reciprocidad (¿es correspondido?)
Historia     (eventos compartidos)
```

Esto es lo que hace que una muerte **importe**: el dolor se propaga por la red proporcional a la fuerza del vínculo.

---

# Regla Principal del Sistema — REVISADA

La v1 decía "maximizar bienestar". La v2 dice:

> Todos los agentes intentan **satisfacer** su bienestar — no optimizarlo.

Eligen la primera opción "suficientemente buena" según sus pesos personales, con información incompleta y sesgada por la emoción del momento, sujeto a restricciones de **dinero, tiempo y energía**.

Los optimizadores globales perfectos se ven robóticos e idénticos. La racionalidad acotada es lo que produce diversidad de conducta.

---

# Ciclo de Simulación — REVISADO

## Escalas de tiempo múltiples

La v1 fijaba "1 tick = 1 hora" como ley única. La v2 usa escalas distintas según el proceso:

```text
Tick horario      → conducta individual, energía, rutinas
Paso diario       → finanzas del hogar, contratos
Paso mensual      → economía agregada, mercado laboral
Paso poblacional  → demografía (nacimientos, muertes, envejecimiento)
```

## Durante cada tick horario

1. Actualizar estado de personas (incluye recalcular emoción y decaerla).
2. Evaluación (appraisal): comparar esperado vs real.
3. Decidir acción (satisfacer, sesgado por rasgos + emoción).
4. Ejecutar acción sobre el mundo.
5. Procesar eventos y propagarlos a memorias y red social.
6. Actualizar hogares, economía y movilidad en su escala correspondiente.

---

# El Bucle del Agente — NUEVO

```text
ENTRADAS                COGNICIÓN              SALIDA
Rasgos (fijo)      ┐
Necesidades        ├──→  Evaluación  ──→  Emoción  ──→  Decisión  ──→  Acción
Memoria (acumula)  ┘                                                      │
       ▲                                                                  ▼
       └──────────────  se vuelve memoria  ◀───────  Mundo + Eventos  ◀──┘
```

La heterogeneidad nace de combinar tres escalas: rasgo (fijo), memoria (acumula), emoción (decae). Dos agentes idénticos hoy actúan distinto porque vivieron cosas distintas.

---

# Recursos Fundamentales

## Dinero
Aumenta con trabajo, negocios e inversiones. Disminuye con consumo, transporte, vivienda y salud.

## Tiempo
Recurso limitado. Toda actividad lo consume.

## Energía
Fatiga física y mental. Se recupera con sueño, descanso y vacaciones. Se consume con trabajo, estudio, traslados y estrés.

## Bienestar — REVISADO
Indicador global de calidad de vida. En la v2 depende de:

```text
Salud
Satisfacción de necesidades psicológicas (pertenencia, autonomía, propósito, seguridad, estímulo)
Relaciones (calidad y cantidad de vínculos activos)
Economía
Descanso
```

Ponderado por los rasgos del agente. Un agente sociable sufre más el aislamiento; uno ambicioso, el estancamiento.

---

# Sistema de Causalidad — CONSERVADO Y AMPLIADO

No almacenar estados psicológicos arbitrarios. Los estados emocionales emergen de condiciones observables.

```text
Incorrecto:  Persona triste
Correcto:    Desempleo + bajos ingresos + problemas familiares → ↓ bienestar
Ampliado:    + alta resiliencia → recuperación más rápida
             + bajo apoyo social → recuperación más lenta y contagio al hogar
```

---

# Emoción Transitoria — NUEVO

Señales de corta duración que emergen de la brecha entre expectativa y resultado:

```text
Perdí algo que esperaba conservar   → pena
Logré algo improbable               → euforia
Esperaba ayuda y no llegó           → frustración
```

- Sesgan las decisiones **mientras duran**.
- **Decaen** con el tiempo; la velocidad de decaimiento la fija el rasgo de resiliencia.
- Nunca se almacenan como estado fijo: se recalculan cada tick.

---

# Contagio Social — NUEVO

Estados de ánimo y conductas se difunden por la red de relaciones, con intensidad proporcional a la fuerza del vínculo.

De aquí emergen los **fenómenos colectivos**: olas de pesimismo en un barrio golpeado económicamente, optimismo que se propaga, pánico, modas. Es la pieza que conecta lo individual con lo emergente-colectivo de la visión.

---

# Sistema de Muerte — NUEVO

En la v1 la muerte sería un `delete` con un ajuste de ingresos. En la v2 es un sistema con cola larga de consecuencias.

## La muerte emerge, no se agenda

```text
Riesgo acumulado de salud:  edad + hábitos + estrés sostenido + acceso a salud
Eventos agudos:             accidentes (según seguridad / movilidad)
Factores de riesgo:         aislamiento prolongado, bienestar crónicamente bajo
```

> Los factores psicosociales entran como **uno más entre varios** factores de riesgo de salud, tratados con sobriedad. No se modela un "la tristeza mata" mecánico.

## Efectos posteriores (lo que la hace pesar)

```text
Duelo            en los conectados, escalado por fuerza del vínculo,
                 decae según la resiliencia de cada uno
Vacante de rol   ¿quién hace el trabajo? ¿quién cuida a los hijos?
Shock económico  pérdida de ingresos + herencia
Hogar            reestructuración o disolución, posible mudanza
Huella           la memoria del fallecido sigue afectando decisiones de los vivos
Macro            cambia la pirámide poblacional → mercado laboral → economía
```

La muerte deja de ser un borrado y se vuelve un sistema cuyas consecuencias se propagan en el tiempo y en la red.

---

# Evolución Temporal y Persistencia Offline — REVISADO

La ciudad sigue evolucionando aunque el usuario cierre la sesión. Al reingresar **no** se simulan todos los segundos transcurridos: se calcula un estado consistente proyectado.

```text
Usuario sale:  1 junio 2026
Usuario vuelve: 10 junio 2026
La simulación calcula los efectos acumulados de esos días.
```

## Estrategia de proyección (mayor riesgo técnico del proyecto)

Separar procesos por naturaleza y proyectar cada uno con su método:

```text
Deterministas (calculables en salto):
  envejecimiento, contratos, pagos recurrentes, demografía base

Estocásticos (muestreados, no simulados tick a tick):
  accidentes, encuentros sociales, eventos de salud agudos
```

---

# Capas — REVISADO (módulos activables, no fases)

Implementar como flags para validar el MVP con la Capa 1 activa y encender el resto sin reescribir el motor.

```text
Capa 1  Personas · Hogares · Trabajo · Movilidad
Capa 2  Ingresos · Gastos · Ahorro · Comercio
Capa 3  Clima · Consumo energético · Agua · Gas · Electricidad
Capa 4  Relaciones · Amistades · Parejas · Redes de apoyo
Capa 5  Salud física · Salud mental · Hábitos
Capa 6  Seguridad · Accidentes · Infracciones · Patrullas · Cámaras
```

---

# Observadores

La simulación es única; las vistas cambian según el rol.

```text
Ciudadano          Trabajo · Familia · Transporte
Policía            Incidentes · Patrullas · Alertas
Operador Cámaras   Eventos · Monitoreo · Flujos urbanos
Empresa            Clientes · Demanda · Costos
Analista Urbano    Movilidad · Energía · Economía · Demografía
```

---

# Principio de Escalabilidad — CONSERVADO

No simular todo al máximo detalle. Usar niveles de abstracción:

```text
Nivel 1  Estadísticas agregadas
Nivel 2  Hogares
Nivel 3  Personas individuales
Nivel 4  Personas activas cerca del usuario
```

La complejidad sube solo cuando es necesario.

---

# MVP Inicial

## Escala

```text
100 personas · 30 hogares · 20 empresas · 1 barrio
```

Objetivo: simular un año completo de evolución social, económica y laboral.

## Orden de implementación recomendado — NUEVO

El riesgo de agregar todo de golpe es no poder distinguir emergencia genuina de un bug. Encender por etapas y validar entre cada una:

```text
1. Motor base + rasgos + necesidades no económicas
   → Validar: ¿los agentes se ven distintos entre sí?
2. Memoria episódica + objetivos dinámicos
   → Validar: ¿el pasado cambia el presente?
3. Emoción transitoria + decisión satisfaciente
   → Validar: ¿hay irracionalidad creíble?
4. Relaciones con peso + contagio social
   → Validar: ¿emergen fenómenos colectivos?
5. Sistema de muerte completo
   → Validar: ¿una muerte genera ondas en la red y la economía?
```

---

# Meta Final

Construir una ciudad persistente donde las personas nacen, trabajan, estudian, forman relaciones, consumen recursos, envejecen, **recuerdan, sienten, deciden con sesgo**, influyen en otros, modifican la economía, transforman barrios, generan fenómenos colectivos y mueren dejando huella.

Todo a partir de reglas simples y consistentes.

> La ciudad no existe para el jugador. El jugador existe dentro de la ciudad.
