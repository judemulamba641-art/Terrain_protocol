# tests/simulations/metrics.py

import time
import numpy as np
from collections import defaultdict


class MetricsCollector:
    """
    Collecteur central de métriques du protocole
    (économiques, sécurité, stress, cartographie 3D)
    """

    def __init__(self):
        self.start_time = time.time()

        self.counters = defaultdict(int)
        self.values = defaultdict(list)
        self.snapshots = []

        # Terrain / NFT metrics
        self.terrain_maps = []

    # -----------------------------
    # BASIC METRICS
    # -----------------------------

    def inc(self, key: str, value: int = 1):
        self.counters[key] += value

    def record(self, key: str, value: float):
        self.values[key].append(value)

    def snapshot(self, label: str):
        self.snapshots.append({
            "time": time.time() - self.start_time,
            "label": label,
            "counters": dict(self.counters),
            "averages": {
                k: float(np.mean(v)) if v else 0.0
                for k, v in self.values.items()
            }
        })

    # -----------------------------
    # TERRAIN / NFT METRICS
    # -----------------------------

    def record_terrain_map(
        self,
        z_values: np.ndarray,
        health_factor: np.ndarray
    ):
        """
        Stocke un snapshot de la carte NFT 3D
        """
        self.terrain_maps.append({
            "avg_value": float(np.mean(z_values)),
            "min_value": float(np.min(z_values)),
            "avg_health_factor": float(np.mean(health_factor)),
            "liquidation_zones": int((health_factor < 1.3).sum())
        })

    # -----------------------------
    # EXPORT
    # -----------------------------

    def export(self) -> dict:
        return {
            "runtime": time.time() - self.start_time,
            "counters": dict(self.counters),
            "metrics": {
                k: {
                    "avg": float(np.mean(v)),
                    "min": float(np.min(v)),
                    "max": float(np.max(v)),
                }
                for k, v in self.values.items()
            },
            "terrain_maps": self.terrain_maps,
            "snapshots": self.snapshots
  }
