"""
Price Volatility Simulation
---------------------------

Simulation de forte volatilité des prix NFT.
Analyse l'impact des oscillations de prix sur :
- health factors
- liquidations
- stabilité du pool
"""

import random

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.metrics import MetricsRegistry
from tests.simulations.reports.report_generator import SimulationReportGenerator


# ============================================================
# Oracle volatility agent
# ============================================================

class OracleVolatilityAgent:
    """
    Agent simulant une forte volatilité de prix NFT.
    """

    def __init__(self, base_price, volatility_pct=0.15):
        self.base_price = base_price
        self.volatility = volatility_pct
        self.current_price = base_price

    def on_tick(self, engine: SimulationEngine):
        # Random walk
        delta = random.uniform(
            -self.volatility,
            self.volatility
        )

        self.current_price *= (1 + delta)

        oracle = engine.context.protocol["oracle"]
        oracle.setPrice(self.current_price)

        engine.context.metrics_registry.record(
            "nft_price",
            engine.current_time(),
            self.current_price
        )


# ============================================================
# Borrower health monitor agent
# ============================================================

class HealthMonitorAgent:
    """
    Observe les health factors et déclenche des métriques.
    """

    def __init__(self, borrowers):
        self.borrowers = borrowers

    def on_tick(self, engine: SimulationEngine):
        pool = engine.context.protocol["lending_pool"]

        for user in self.borrowers:
            hf = pool.healthFactor(user)

            engine.context.metrics_registry.record(
                "health_factor",
                engine.current_time(),
                hf
            )

            if hf < 1:
                engine.context.metrics_registry.inc(
                    "health_factor_below_one"
                )


# ============================================================
# Opportunistic liquidator agent
# ============================================================

class OpportunisticLiquidatorAgent:
    """
    Liquidateur opportuniste sous volatilité.
    """

    def __init__(self, max_liquidations_per_tick=3):
        self.capacity = max_liquidations_per_tick

    def on_tick(self, engine: SimulationEngine):
        pool = engine.context.protocol["lending_pool"]
        count = 0

        for borrower in pool.getUnderwaterBorrowers():
            if count >= self.capacity:
                break

            pool.liquidate(borrower)
            count += 1

            engine.context.metrics_registry.inc("liquidations")

        if count > 0:
            engine.context.metrics_registry.record(
                "liquidations_per_tick",
                engine.current_time(),
                count
            )


# ============================================================
# Simulation runner
# ============================================================

def run_price_volatility_simulation(
    protocol,
    borrowers,
    base_price,
    duration=300
):
    """
    Lance la simulation de volatilité des prix.
    """

    engine = SimulationEngine(protocol=protocol)
    engine.context.metrics_registry = MetricsRegistry()

    engine.register_agent(
        OracleVolatilityAgent(base_price)
    )

    engine.register_agent(
        HealthMonitorAgent(borrowers)
    )

    engine.register_agent(
        OpportunisticLiquidatorAgent()
    )

    pool = protocol["lending_pool"]

    # Initial metrics
    engine.context.metrics_registry.set_gauge(
        "initial_liquidity",
        pool.totalLiquidity()
    )

    # Run simulation
    engine.run(duration=duration)

    # Final metrics
    engine.context.metrics_registry.set_gauge(
        "final_liquidity",
        pool.totalLiquidity()
    )

    engine.context.metrics_registry.set_gauge(
        "protocol_solvency",
        pool.isSolvent()
    )

    # Generate report
    report = SimulationReportGenerator(
        engine.context.metrics_registry.snapshot()
    )

    return report.generate()


# ============================================================
# Standalone execution (research mode)
# ============================================================

if __name__ == "__main__":
    # Minimal mock protocol for volatility research
    class MockOracle:
        def __init__(self):
            self.price = 0

        def setPrice(self, price):
            self.price = price

    class MockPool:
        def __init__(self, borrowers):
            self.borrowers = borrowers
            self.liquidity = 1_200_000
            self.underwater = set()

        def totalLiquidity(self):
            return self.liquidity

        def isSolvent(self):
            return self.liquidity > 0

        def healthFactor(self, user):
            # Simulate noisy HF
            hf = random.uniform(0.7, 1.3)
            if hf < 1:
                self.underwater.add(user)
            return hf

        def getUnderwaterBorrowers(self):
            return list(self.underwater)

        def liquidate(self, user):
            if user in self.underwater:
                self.underwater.remove(user)

    borrowers = [f"0xB{i}" for i in range(10)]

    protocol = {
        "oracle": MockOracle(),
        "lending_pool": MockPool(borrowers)
    }

    report = run_price_volatility_simulation(
        protocol=protocol,
        borrowers=borrowers,
        base_price=100_000
    )

    print("\n=== PRICE VOLATILITY REPORT ===")
    print(report)