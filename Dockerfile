# syntax=docker/dockerfile:1
#
# Imagen multi-stage para la simulación urbana persistente (citysim).
#   - builder : instala el paquete en un venv aislado.
#   - test    : target opcional que corre la suite con pytest (CI / `make test`).
#   - runtime : imagen final mínima, sin toolchain, usuario no-root.
#
# Build de la imagen de ejecución:   docker build -t citysim .
# Correr la suite de tests:          docker build --target test .

ARG PYTHON_VERSION=3.12

# ---------------------------------------------------------------------------
# Base común: variables de entorno saludables para Python en contenedor.
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# ---------------------------------------------------------------------------
# Builder: crea un venv e instala el paquete. Se copia primero la metadata
# para aprovechar el cache de capas cuando solo cambia el código fuente.
# ---------------------------------------------------------------------------
FROM base AS builder
RUN python -m venv /opt/venv
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

# ---------------------------------------------------------------------------
# Test: hereda el venv del builder, agrega dependencias de desarrollo y corre
# la suite. Útil como `docker build --target test` o servicio de compose.
# ---------------------------------------------------------------------------
FROM builder AS test
RUN pip install ".[dev]"
COPY tests ./tests
RUN pytest

# ---------------------------------------------------------------------------
# Runtime: imagen final mínima. Solo copia el venv ya instalado (no el
# toolchain de build) y corre como usuario no-root.
# ---------------------------------------------------------------------------
FROM base AS runtime
LABEL org.opencontainers.image.title="citysim" \
      org.opencontainers.image.description="Simulación urbana persistente: una sociedad artificial emergente" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/RenatoAntonioCL/simulacion-urbana"

RUN useradd --create-home --uid 1000 sim
COPY --from=builder /opt/venv /opt/venv
USER sim

# Por defecto corre un año completo de simulación; se puede sobreescribir:
#   docker run --rm citysim --days 30 --seed 7
ENTRYPOINT ["python", "-m", "citysim"]
CMD ["--days", "365"]
