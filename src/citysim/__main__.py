"""Punto de entrada: corre un run del MVP y reporta invariantes.

    python -m citysim            # run por defecto (seed 42, 1 año)
    python -m citysim --days 30  # run corto
"""

from __future__ import annotations

import argparse

from . import invariants
from .config import SimConfig
from .eventlog.log import EventLog
from .scheduler.clock import Scheduler
from .seed.seeder import seed_world


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulación urbana persistente (MVP)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--days", type=int, default=None, help="días a simular (def: config)")
    args = parser.parse_args()

    config = SimConfig(seed=args.seed)
    world = seed_world(config)
    log = EventLog()

    invariants.check_all(world, log)  # estado inicial sano

    scheduler = Scheduler(config)
    scheduler.run(world, log, days=args.days)

    invariants.check_all(world, log)  # estado final sano (incl. conservación de dinero)

    print(f"seed={config.seed} días={args.days or config.sim_days}")
    print(f"personas={len(world.persons)} hogares={len(world.households)} lugares={len(world.places)}")
    print(f"eventos registrados={len(log)}")
    print(f"huella del log={log.fingerprint()[:16]}…")


if __name__ == "__main__":
    main()
