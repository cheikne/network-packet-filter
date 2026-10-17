# Short commands for the lab. Run them from the repository root.
# Type "make" to see the list.

COMPOSE = docker compose -f infra/docker-compose.yml

# Default values for the commands that take a parameter
N ?= fw         # node for "make shell"
P ?= baseline   # policy for "make policy"
C ?= baseline   # configuration for "make run"
S ?= A          # scenario for "make run"
R ?= 1          # repetitions for "make run"
D ?=            # duration in seconds for "make run" (empty = from experiments.yaml)

.PHONY: help setup up down status logs test shell policy run

help:
	@echo "make setup                     first-time setup and checks"
	@echo "make up                        build and start the lab"
	@echo "make down                      stop the lab"
	@echo "make status                    show the running nodes"
	@echo "make logs                      show the nodes' startup logs"
	@echo "make test                      check connectivity and tools"
	@echo "make shell N=fw                open a shell on a node (fw, server, legit, susp)"
	@echo "make policy P=p1_basic         load policies/<P>.nft into fw (baseline = no rules)"
	@echo "make run C=baseline S=A R=1    run an experiment (add D=10 for a short run)"

setup:
	@test -f infra/.env || { cp infra/.env.example infra/.env; echo "Created infra/.env"; }
	@! grep -q "change-me" infra/.env || echo "Warning: set LAB_SSH_USER and LAB_SSH_PASSWORD in infra/.env"
	@docker info >/dev/null 2>&1 || { echo "Docker is not running: start Docker Desktop"; exit 1; }
	@python3 -c "import yaml" 2>/dev/null || { echo "PyYAML is missing: pip3 install pyyaml"; exit 1; }
	@echo "Setup OK. Next: make up"

up:
	@test -f infra/.env || { echo "infra/.env is missing: run make setup first"; exit 1; }
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

status:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs

test:
	./infra/tests/connectivity.sh
	./infra/tests/tools.sh

shell:
	docker exec -it $(strip $(N)) bash

policy:
	./automation/apply_policy.sh $(strip $(P))

run:
	python3 automation/run_experiment.py --config $(strip $(C)) --scenario $(strip $(S)) \
	  --reps $(strip $(R)) $(if $(strip $(D)),--duration $(strip $(D)))
