# Atajos para trabajar con el proyecto vía Docker.
# `make help` lista los objetivos disponibles.

IMAGE ?= citysim
DAYS  ?= 365
SEED  ?= 42

.DEFAULT_GOAL := help

.PHONY: help build run test shell lint clean

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

build: ## Construye la imagen de ejecución (target runtime)
	docker build --target runtime -t $(IMAGE):latest .

run: build ## Corre la simulación (vars: DAYS, SEED)
	docker run --rm -v "$(PWD)/runs:/app/runs" $(IMAGE):latest --days $(DAYS) --seed $(SEED)

test: ## Corre la suite de tests dentro de Docker
	docker build --target test -t $(IMAGE):test .

shell: build ## Abre una shell dentro del contenedor de ejecución
	docker run --rm -it --entrypoint /bin/bash $(IMAGE):latest

clean: ## Elimina imágenes y artefactos locales
	-docker image rm $(IMAGE):latest $(IMAGE):test 2>/dev/null || true
	rm -rf runs
