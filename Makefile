# Atajos para trabajar con el proyecto.
# `make help` lista los objetivos disponibles.
# Targets locales (ui, venv, lint) usan un venv de Python; el resto va vía Docker.

IMAGE   ?= citysim
DAYS    ?= 365
SEED    ?= 42

# Entorno local. Python 3.12: pygame 2.6.1 no inicia en 3.14 (bug de import en font).
PYTHON  ?= python3.12
VENV    ?= .venv
VENV_PY := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help ui venv lint build run test shell clean

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

# ── Local (sin Docker) ──────────────────────────────────────────────────────

ui: venv ## Abre el cliente de escritorio (crea el venv si falta)
	$(VENV_PY) -m citysim_desktop

venv: ## Crea el venv local (Python 3.12) e instala el cliente, si falta
	@test -x $(VENV_PY) || ( \
		$(PYTHON) -m venv $(VENV) && \
		$(VENV_PY) -m pip install --upgrade pip && \
		$(VENV_PY) -m pip install -e ".[dev,ui]" )

lint: venv ## Corre ruff sobre el código (usa el venv local)
	$(VENV_PY) -m ruff check src tests

# ── Docker ──────────────────────────────────────────────────────────────────

build: ## Construye la imagen de ejecución (target runtime)
	docker build --target runtime -t $(IMAGE):latest .

run: build ## Corre la simulación headless (vars: DAYS, SEED)
	docker run --rm -v "$(PWD)/runs:/app/runs" $(IMAGE):latest --days $(DAYS) --seed $(SEED)

test: ## Corre la suite de tests dentro de Docker
	docker build --target test -t $(IMAGE):test .

shell: build ## Abre una shell dentro del contenedor de ejecución
	docker run --rm -it --entrypoint /bin/bash $(IMAGE):latest

clean: ## Elimina imágenes y artefactos locales
	-docker image rm $(IMAGE):latest $(IMAGE):test 2>/dev/null || true
	rm -rf runs
