"""
Time Machine
------------

Outil de contrôle du temps simulé et de snapshots.
Permet d'avancer, sauvegarder et restaurer l'état
temporel d'une simulation.

Utilisé pour :
- backtesting
- fuzz temporel
- scénarios alternatifs
- replay déterministe
"""

import copy
from typing import Any, Dict


# ============================================================
# Time snapshot
# ============================================================

class TimeSnapshot:
    """
    Snapshot complet du temps et de l'état associé.
    """

    def __init__(
        self,
        timestamp: int,
        scheduler_state: Any,
        simulation_state: Dict[str, Any],
        metrics: Dict[str, Any],
    ):
        self.timestamp = timestamp
        self.scheduler_state = scheduler_state
        self.simulation_state = simulation_state
        self.metrics = metrics


# ============================================================
# Time machine
# ============================================================

class TimeMachine:
    """
    Machine à remonter le temps pour simulations.

    Fonctionne uniquement sur du temps simulé.
    """

    def __init__(self, scheduler, context):
        """
        scheduler : EventScheduler
        context   : SimulationContext
        """
        self.scheduler = scheduler
        self.context = context
        self.snapshots = []

    # ------------------
    # Time travel
    # ------------------

    def now(self) -> int:
        return self.scheduler.current_time

    def advance(self, seconds: int):
        """
        Avance le temps simulé.
        """
        self.scheduler.advance_time(seconds)

    # ------------------
    # Snapshots
    # ------------------

    def snapshot(self) -> TimeSnapshot:
        """
        Crée un snapshot complet de la simulation.
        """
        snap = TimeSnapshot(
            timestamp=self.scheduler.current_time,
            scheduler_state=copy.deepcopy(self.scheduler),
            simulation_state=copy.deepcopy(self.context.state),
            metrics=copy.deepcopy(self.context.metrics),
        )

        self.snapshots.append(snap)
        return snap

    def restore(self, snapshot: TimeSnapshot):
        """
        Restaure un snapshot précédent.
        """
        self.scheduler = copy.deepcopy(snapshot.scheduler_state)
        self.context.state = copy.deepcopy(snapshot.simulation_state)
        self.context.metrics = copy.deepcopy(snapshot.metrics)

    # ------------------
    # Branching
    # ------------------

    def fork_from_snapshot(self, snapshot: TimeSnapshot):
        """
        Crée une nouvelle TimeMachine à partir d'un snapshot.
        """
        forked_scheduler = copy.deepcopy(snapshot.scheduler_state)
        forked_context = copy.deepcopy(self.context)

        forked_context.state = copy.deepcopy(snapshot.simulation_state)
        forked_context.metrics = copy.deepcopy(snapshot.metrics)

        return TimeMachine(
            scheduler=forked_scheduler,
            context=forked_context
        )

    # ------------------
    # Introspection
    # ------------------

    def snapshot_count(self) -> int:
        return len(self.snapshots)

    def last_snapshot(self) -> TimeSnapshot:
        if not self.snapshots:
            return None
        return self.snapshots[-1]