"""
Governance Attack Simulation
----------------------------

Simulation d'une attaque de gouvernance :
un acteur malveillant capture la DAO,
modifie un paramètre critique et observe
l'impact sur la solvabilité du protocole.
"""

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.metrics import MetricsRegistry
from tests.simulations.reports.report_generator import SimulationReportGenerator


# ============================================================
# Malicious governance agent
# ============================================================

class MaliciousGovernanceAgent:
    """
    Agent simulant une attaque de gouvernance.
    """

    def __init__(self, attacker_account):
        self.attacker = attacker_account

    def on_register(self, engine: SimulationEngine):
        engine.context.metrics_registry.set_metadata(
            "attack_type",
            "governance_capture"
        )

        # Schedule malicious proposal
        engine.schedule_event(
            delay=10,
            callback=self.propose_attack,
            description="Malicious governance proposal"
        )

        # Schedule execution
        engine.schedule_event(
            delay=100,
            callback=self.execute_attack,
            description="Execute malicious proposal"
        )

    def propose_attack(self, context, _payload):
        # Extreme liquidation bonus (e.g. +40%)
        context.state["proposed_liquidation_bonus"] = 14000
        context.metrics_registry.inc("governance_proposals")
        print("[ATTACK] Malicious proposal submitted")

    def execute_attack(self, context, _payload):
        bonus = context.state.get("proposed_liquidation_bonus")
        context.state["liquidation_bonus"] = bonus
        context.metrics_registry.inc("governance_executions")
        print(f"[ATTACK] Proposal executed: liquidation bonus = {bonus}")


# ============================================================
# Simulation scenario
# ============================================================

def run_governance_attack_simulation(protocol):
    """
    Lance la simulation complète d'attaque de gouvernance.
    """

    engine = SimulationEngine(protocol=protocol)
    engine.context.metrics_registry = MetricsRegistry()

    attacker = protocol["accounts"]["attacker"]

    engine.register_agent(
        MaliciousGovernanceAgent(attacker)
    )

    # Initial protocol state
    engine.context.state["liquidation_bonus"] = 10500  # 5%
    engine.context.metrics_registry.set_gauge(
        "initial_liquidation_bonus",
        10500
    )

    # Run simulation
    engine.run(duration=200)

    # Final metrics
    engine.context.metrics_registry.set_gauge(
        "final_liquidation_bonus",
        engine.context.state["liquidation_bonus"]
    )

    engine.context.metrics_registry.set_gauge(
        "protocol_solvency",
        protocol["lending_pool"].isSolvent()
    )

    # Generate report
    report = SimulationReportGenerator(
        engine.context.metrics_registry.snapshot()
    )

    return report.generate()


# ============================================================
# Standalone execution (optional)
# ============================================================

if __name__ == "__main__":
    # Mock protocol context for research runs
    protocol = {
        "accounts": {
            "attacker": "0xATTACKER"
        },
        "lending_pool": type(
            "MockPool",
            (),
            {"isSolvent": lambda self=True: True}
        )()
    }

    report = run_governance_attack_simulation(protocol)

    print("\n=== GOVERNANCE ATTACK REPORT ===")
    print(report)