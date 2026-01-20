"""
Simulation Engine
-----------------

Moteur central de simulation pour le protocole DeFi.

Responsabilités :
- orchestration du temps
- gestion des agents
- exécution d'événements
- collecte de métriques

Aucune logique métier on-chain ici.
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field

from tests.simulations.engine.event_scheduler import EventScheduler


# ============================================================
# Simulation context
# ============================================================

@dataclass
class SimulationContext:
    """
    Contexte partagé entre tous les agents et événements.
    """
    protocol: Dict[str, Any]
    metrics: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Agent base class
# ============================================================

class SimulationAgent:
    """
    Classe de base pour tous les agents de simulation.
    """

    def __init__(self, name: str):
        self.name = name

    def on_register(self, engine: "SimulationEngine"):
        """
        Hook appelé lors de l'enregistrement de l'agent.
        """
        pass

    def on_tick(self, engine: "SimulationEngine"):
        """
        Hook appelé à chaque tick de temps.
        """
        pass


# ============================================================
# Simulation engine
# ============================================================

class SimulationEngine:
    """
    Orchestrateur principal de la simulation.
    """

    def __init__(
        self,
        protocol: Dict[str, Any],
        start_time: int = 0
    ):
        self.scheduler = EventScheduler(start_time=start_time)
        self.context = SimulationContext(protocol=protocol)
        self.agents: List[SimulationAgent] = []
        self.tick_interval = 1  # seconde simulée

        self.context.metrics["events_executed"] = 0
        self.context.metrics["ticks"] = 0

    # ------------------
    # Agent management
    # ------------------

    def register_agent(self, agent: SimulationAgent):
        self.agents.append(agent)
        agent.on_register(self)

    # ------------------
    # Event scheduling
    # ------------------

    def schedule_event(
        self,
        delay: int,
        callback: Callable,
        description: str = "",
        payload: Any = None
    ):
        def wrapped_callback(payload=payload):
            callback(self.context, payload)
            self.context.metrics["events_executed"] += 1

        self.scheduler.schedule(
            delay=delay,
            callback=wrapped_callback,
            description=description,
            payload=payload
        )

    # ------------------
    # Time progression
    # ------------------

    def run(self, duration: int):
        """
        Lance la simulation pour une durée donnée.
        """
        end_time = self.scheduler.current_time + duration

        while self.scheduler.current_time < end_time:
            self._tick()
            self.scheduler.advance_time(self.tick_interval)

    def run_until_event_empty(self):
        """
        Exécute jusqu'à épuisement des événements.
        """
        while self.scheduler.pending_events() > 0:
            self._tick()
            next_time = self.scheduler.next_event_time()
            self.scheduler.run_until(next_time)

    def _tick(self):
        self.context.metrics["ticks"] += 1
        for agent in self.agents:
            agent.on_tick(self)

    # ------------------
    # Introspection
    # ------------------

    def current_time(self) -> int:
        return self.scheduler.current_time

    def metrics(self) -> Dict[str, Any]:
        return self.context.metrics

    def state(self) -> Dict[str, Any]:
        return self.context.state