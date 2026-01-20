"""
Event Scheduler Engine
----------------------

Moteur d'événements déterministe pour simulations DeFi.

Utilisé pour :
- market crash
- cascades de liquidation
- délais oracle
- bots keeper
- stress tests

Aucune logique métier ici.
Seulement du temps + des événements.
"""

import heapq
import time
from typing import Callable, Any


# ============================================================
# Event definition
# ============================================================

class ScheduledEvent:
    """
    Représente un événement planifié dans le temps.
    """

    def __init__(
        self,
        timestamp: int,
        callback: Callable,
        description: str = "",
        payload: Any = None
    ):
        self.timestamp = timestamp
        self.callback = callback
        self.description = description
        self.payload = payload

    def __lt__(self, other):
        return self.timestamp < other.timestamp


# ============================================================
# Scheduler
# ============================================================

class EventScheduler:
    """
    Scheduler déterministe basé sur une priority queue.

    Le temps est simulé (pas wall-clock).
    """

    def __init__(self, start_time: int = 0):
        self.current_time = start_time
        self._queue = []

    # ------------------
    # Event management
    # ------------------

    def schedule(
        self,
        delay: int,
        callback: Callable,
        description: str = "",
        payload: Any = None
    ):
        """
        Planifie un événement après `delay` secondes.
        """
        event_time = self.current_time + delay

        event = ScheduledEvent(
            timestamp=event_time,
            callback=callback,
            description=description,
            payload=payload
        )

        heapq.heappush(self._queue, event)

    def schedule_at(
        self,
        timestamp: int,
        callback: Callable,
        description: str = "",
        payload: Any = None
    ):
        """
        Planifie un événement à un timestamp précis.
        """
        event = ScheduledEvent(
            timestamp=timestamp,
            callback=callback,
            description=description,
            payload=payload
        )

        heapq.heappush(self._queue, event)

    # ------------------
    # Time control
    # ------------------

    def advance_time(self, seconds: int):
        """
        Avance le temps simulé.
        """
        self.current_time += seconds
        self._execute_due_events()

    def run_until(self, timestamp: int):
        """
        Avance le temps jusqu'à un timestamp donné.
        """
        if timestamp < self.current_time:
            raise ValueError("Cannot go back in time")

        self.current_time = timestamp
        self._execute_due_events()

    def run_all(self):
        """
        Exécute tous les événements restants.
        """
        while self._queue:
            event = heapq.heappop(self._queue)
            self.current_time = event.timestamp
            self._execute_event(event)

    # ------------------
    # Internal execution
    # ------------------

    def _execute_due_events(self):
        while self._queue and self._queue[0].timestamp <= self.current_time:
            event = heapq.heappop(self._queue)
            self._execute_event(event)

    def _execute_event(self, event: ScheduledEvent):
        try:
            if event.payload is not None:
                event.callback(event.payload)
            else:
                event.callback()
        except Exception as e:
            raise RuntimeError(
                f"Event execution failed: {event.description}"
            ) from e

    # ------------------
    # Introspection
    # ------------------

    def pending_events(self) -> int:
        return len(self._queue)

    def next_event_time(self):
        if not self._queue:
            return None
        return self._queue[0].timestamp