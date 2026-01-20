"""
Simulation Metrics
------------------

Collecteur structuré de métriques pour simulations DeFi.

Responsabilités :
- enregistrer des événements chiffrés
- agréger des séries temporelles
- exposer des métriques finales exploitables

Aucune logique métier.
"""

from collections import defaultdict
from typing import Dict, List, Any


class MetricsRegistry:
    """
    Registre central des métriques de simulation.
    """

    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = {}
        self.time_series = defaultdict(list)
        self.metadata = {}

    # ------------------
    # Counters
    # ------------------

    def inc(self, name: str, value: int = 1):
        self.counters[name] += value

    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)

    # ------------------
    # Gauges (last value)
    # ------------------

    def set_gauge(self, name: str, value: Any):
        self.gauges[name] = value

    def get_gauge(self, name: str):
        return self.gauges.get(name)

    # ------------------
    # Time series
    # ------------------

    def record(
        self,
        name: str,
        timestamp: int,
        value: Any
    ):
        self.time_series[name].append(
            {
                "time": timestamp,
                "value": value
            }
        )

    def get_series(self, name: str) -> List[Dict[str, Any]]:
        return self.time_series.get(name, [])

    # ------------------
    # Metadata
    # ------------------

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def snapshot(self) -> Dict[str, Any]:
        """
        Snapshot complet des métriques.
        """
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "time_series": dict(self.time_series),
            "metadata": dict(self.metadata),
        }