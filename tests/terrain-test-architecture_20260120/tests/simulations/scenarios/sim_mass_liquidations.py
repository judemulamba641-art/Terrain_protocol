"""
Mass Liquidation Simulation
---------------------------

Simulation d'un événement de liquidations en masse.
Analyse les cascades de liquidations et la résilience
du pool de lending sous stress extrême.
"""

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.metrics import MetricsRegistry
from tests.simulations.reports.report_generator import SimulationReportGenerator


# ============================================================
# Borrower swarm agent
# ============================================================

class BorrowerSwarmAgent:
    """
    Agent représentant un groupe de borrowers similaires.
    """

    def __init__(self, borrowers):
        self.borrowers = borrowers

    def on_register(self, engine: SimulationEngine):
        # Tous les borrowers ouvrent une position
        engine.schedule_event(
            delay=5,
            callback=self.open_positions,
            description="Borrowers open positions"
        )

        # Choc de prix global
        engine.schedule_event(
            delay=50,
            callback=self.market_crash,
            description="Global NFT price crash"
        )

    def open_positions(self, context, _payload):
        pool = context.protocol["lending_pool"]

        for user in self.borrowers:
            max_borrow = pool.getMaxBorrow(user)
            pool.borrow(user, max_borrow * 0.9)

            context.metrics_registry.inc("borrow_events")

        print(f"[MASS] {len(self.borrowers)} positions opened")

    def market_crash(self, context, _payload):
        # Le crash est abstrait : il se reflète dans le health factor
        context.state["market_crash"] = True
        context.metrics_registry.inc("market_crashes")

        print("[MASS] Market crash triggered")


# ============================================================
# Liquidator swarm agent
# ============================================================

class LiquidatorSwarmAgent:
    """
    Groupe de liquidateurs traitant les positions insolvables.
    """

    def __init__(self, capacity_per_tick=5):
        self.capacity = capacity_per_tick

    def on_tick(self, engine: SimulationEngine):
        pool = engine.context.protocol["lending_pool"]

        liquidated_this_tick = 0

        for borrower in pool.getUnderwaterBorrowers():
            if liquidated_this_tick >= self.capacity:
                break

            pool.liquidate(borrower)
            liquidated_this_tick += 1

            engine.context.metrics_registry.inc("liquidations")

        if liquidated_this_tick > 0:
            engine.context.metrics_registry.record(
                "liquidations_per_tick",
                engine.current_time(),
                liquidated_this_tick
            )


# ============================================================
# Simulation runner
# ============================================================

def run_mass_liquidation_simulation(protocol, borrowers, duration=300):
    """
    Lance la simulation de liquidations en masse.
    """

    engine = SimulationEngine(protocol=protocol)
    engine.context.metrics_registry = MetricsRegistry()

    engine.register_agent(
        BorrowerSwarmAgent(borrowers)
    )

    engine.register_agent(
        LiquidatorSwarmAgent(capacity_per_tick=10)
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
    # Mock protocol for standalone stress testing
    class MockPool:
        def __init__(self, borrowers):
            self.borrowers = borrowers
            self.liquidity = 2_000_000
            self.underwater = set()

        def totalLiquidity(self):
            return self.liquidity

        def isSolvent(self):
            return self.liquidity > 0

        def getMaxBorrow(self, _):
            return 100_000

        def borrow(self, user, amount):
            self.liquidity -= amount
            self.underwater.add(user)

        def getUnderwaterBorrowers(self):
            return list(self.underwater)

        def liquidate(self, user):
            if user in self.underwater:
                self.underwater.remove(user)

    borrowers = [f"0xB{i}" for i in range(30)]

    protocol = {
        "lending_pool": MockPool(borrowers)
    }

    report = run_mass_liquidation_simulation(
        protocol,
        borrowers
    )

    print("\n=== MASS LIQUIDATION REPORT ===")
    print(report)