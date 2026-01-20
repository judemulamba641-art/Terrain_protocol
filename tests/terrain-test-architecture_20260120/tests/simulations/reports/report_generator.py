"""
Simulation Report Generator
---------------------------

Transforme les métriques de simulation
en rapports synthétiques exploitables.

Cible :
- audits
- risk analysis
- DAO governance
- research
"""

from typing import Dict, Any


class SimulationReportGenerator:
    """
    Générateur de rapports de simulation.
    """

    def __init__(self, metrics_snapshot: Dict[str, Any]):
        self.metrics = metrics_snapshot

    # ------------------
    # Executive summary
    # ------------------

    def executive_summary(self) -> Dict[str, Any]:
        counters = self.metrics.get("counters", {})
        gauges = self.metrics.get("gauges", {})

        return {
            "events_executed": counters.get("events_executed", 0),
            "liquidations": counters.get("liquidations", 0),
            "bad_debt_events": counters.get("bad_debt_events", 0),
            "final_pool_liquidity": gauges.get("pool_liquidity"),
            "protocol_solvency": gauges.get("protocol_solvency"),
        }

    # ------------------
    # Risk metrics
    # ------------------

    def risk_metrics(self) -> Dict[str, Any]:
        return {
            "max_liquidations_in_block":
                self._max_in_series("liquidations_per_tick"),
            "worst_health_factor":
                self._min_in_series("health_factor"),
            "price_drawdown":
                self._price_drawdown(),
        }

    # ------------------
    # Time series helpers
    # ------------------

    def _max_in_series(self, name: str):
        series = self.metrics.get("time_series", {}).get(name, [])
        if not series:
            return None
        return max(point["value"] for point in series)

    def _min_in_series(self, name: str):
        series = self.metrics.get("time_series", {}).get(name, [])
        if not series:
            return None
        return min(point["value"] for point in series)

    def _price_drawdown(self):
        series = self.metrics.get("time_series", {}).get("nft_price", [])
        if not series:
            return None

        prices = [p["value"] for p in series]
        peak = max(prices)
        trough = min(prices)

        return (peak - trough) / peak if peak > 0 else None

    # ------------------
    # Full report
    # ------------------

    def generate(self) -> Dict[str, Any]:
        """
        Rapport complet.
        """
        return {
            "summary": self.executive_summary(),
            "risk_metrics": self.risk_metrics(),
            "raw_metrics": self.metrics,
        }