"""
Liquidity Drain Simulation
--------------------------

Simulation d'un scénario de drainage de liquidité.
Analyse la vitesse et l'impact d'un stress économique
sur le pool de lending.
"""

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.metrics import MetricsRegistry
from tests.simulations.reports.report_generator import SimulationReportGenerator


# ============================================================
# Liquidity Drainer Agent
# ============================================================

class LiquidityDrainerAgent:
    """
    Agent simulant une stratégie de drainage de liquidité.
    """

    def __init__(self, borrower_account):
        self.borrower = borrower_account

    def on_register(self, engine: SimulationEngine):
        engine.context.metrics_registry.set_metadata(
            "attack_type",
            "liquidity_drain"
        )

        # Borrow aggressively
        engine.schedule_event(
            delay=5,
            callback=self.borrow_max,
            description="Aggressive borrow"
        )

        # Trigger liquidation loop
        engine.schedule_event(
            delay=30,
            callback=self.trigger_liquidation,
            description="Trigger liquidation"
        )

    def borrow_max(self, context, _payload):
        pool = context.protocol["lending_pool"]
        max_borrow = pool.getMaxBorrow(self.borrower)

        pool.borrow(self.borrower, max_borrow)
        context.metrics_registry.inc("borrow_events")
        context.metrics_registry.record(
            "pool_liquidity",
            context.protocol["time"](),
            pool.totalLiquidity()
        )

        print(f"[DRAIN] Borrowed {max_borrow}")

    def trigger_liquidation(self, context, _payload):
        pool = context.protocol["lending_pool"]

        if pool.healthFactor(self.borrower) < 1:
            pool.liquidate(self.borrower)
            context.metrics_registry.inc("liquidations")

            print("[DRAIN] Liquidation triggered")


# ============================================================
# Passive Lender Agent
# ============================================================

class PassiveLenderAgent:
    """
    Agent représentant des LPs passifs (pas de nouveaux dépôts).
    """

    def on_tick(self, engine: SimulationEngine):
        pool = engine.context.protocol["lending_pool"]
        engine.context.metrics_registry.set_gauge(
            "current_liquidity",
            pool.totalLiquidity()
        )


# ============================================================
# Simulation runner
# ============================================================

def run_liquidity_drain_simulation(protocol, duration=300):
    """
    Lance la simulation de liquidity drain.
    """

    engine = SimulationEngine(protocol=protocol)
    engine.context.metrics_registry = MetricsRegistry()

    attacker = protocol["accounts"]["attacker"]

    engine.register_agent(
        LiquidityDrainerAgent(attacker)
    )

    engine.register_agent(
        PassiveLenderAgent()
    )

    # Initial metrics
    pool = protocol["lending_pool"]

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
    # Minimal mock protocol for standalone runs
    class MockPool:
        def __init__(self):
            self.liquidity = 1_000_000

        def totalLiquidity(self):
            return self.liquidity

        def isSolvent(self):
            return self.liquidity > 0

        def getMaxBorrow(self, _):
            return 400_000

        def borrow(self, _, amount):
            self.liquidity -= amount

        def healthFactor(self, _):
            return 0.8

        def liquidate(self, _):
            pass

    protocol = {
        "accounts": {
            "attacker": "0xDRAINER"
        },
        "lending_pool": MockPool(),
        "time": lambda: 0
    }

    report = run_liquidity_drain_simulation(protocol)

    print("\n=== LIQUIDITY DRAIN REPORT ===")
    print(report)