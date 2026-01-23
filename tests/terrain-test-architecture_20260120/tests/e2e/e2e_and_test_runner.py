# tests/e2e/e2e_and_test_runner.py

import math
import random
import time
import json
from typing import Dict, List

import matplotlib.pyplot as plt

from tests.integration.environment.deploy_protocol import deploy_protocol
from tests.integration.environment.accounts import get_test_accounts

from tests.integration.scenarios.scenario_basic_lending import run_basic_lending
from tests.integration.scenarios.scenario_liquidation import run_liquidation
from tests.integration.scenarios.scenario_governance_change import run_governance_change

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.time_machine import TimeMachine
from tests.simulations.engine.metrics import MetricsCollector


# ============================================================
# CONFIG
# ============================================================

SIMULATED_USERS = 1_000_000_000   # 1 billion
AGENT_BATCH_SIZE = 100_000       # 1 agent = 100k users
TOTAL_AGENTS = SIMULATED_USERS // AGENT_BATCH_SIZE

BLOCKS_PER_DAY = 7200


# ============================================================
# AUDIT TESTS (OFF-CHAIN GUARD RAILS)
# ============================================================

def audit_oracle_sanity(metrics: MetricsCollector):
    assert metrics.oracle_price_deviation < 0.30, "❌ Oracle deviation too high"


def audit_circuit_breaker(metrics: MetricsCollector):
    assert metrics.circuit_breaker_triggered is True, "❌ Circuit breaker never triggered"


def audit_treasury_growth(metrics: MetricsCollector):
    assert metrics.treasury_balance > 0, "❌ Treasury did not accumulate fees"


def audit_governance_delay(metrics: MetricsCollector):
    assert metrics.governance_delay_respected is True, "❌ Governance delay bypassed"


# ============================================================
# MASS USER SIMULATION
# ============================================================

def simulate_billion_users(engine: SimulationEngine, metrics: MetricsCollector):
    print(f"🚀 Simulating {SIMULATED_USERS:,} users using {TOTAL_AGENTS:,} agents")

    for agent_id in range(TOTAL_AGENTS):
        deposit_prob = random.random()
        borrow_prob = random.random()
        liquidate_prob = random.random()

        if deposit_prob > 0.3:
            engine.simulate_deposit(
                users=AGENT_BATCH_SIZE,
                avg_amount=random.uniform(500, 3000)
            )

        if borrow_prob > 0.5:
            engine.simulate_borrow(
                users=AGENT_BATCH_SIZE,
                ltv=random.uniform(0.3, 0.6)
            )

        if liquidate_prob > 0.92:
            engine.simulate_liquidation(
                users=AGENT_BATCH_SIZE * 0.05
            )

        metrics.record_step()

        if agent_id % 500 == 0:
            print(f"  • Agents simulated: {agent_id}/{TOTAL_AGENTS}")

    print("✅ Billion-user simulation completed")


# ============================================================
# GRAPHICS
# ============================================================

def plot_metrics(metrics: MetricsCollector):
    plt.figure(figsize=(14, 8))

    plt.plot(metrics.health_factors, label="Avg Health Factor")
    plt.plot(metrics.total_liquidity, label="Total Liquidity")
    plt.plot(metrics.total_borrowed, label="Total Borrowed")
    plt.plot(metrics.treasury_balance_history, label="Treasury Balance")

    plt.title("Protocol Stress Test Metrics")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    plt.show()


# ============================================================
# MAIN RUNNER
# ============================================================

def main():
    print("\n🧪 FULL E2E + AUDIT TEST RUN\n")

    # --- Environment ---
    accounts = get_test_accounts()
    protocol = deploy_protocol(accounts)

    # --- Integration tests ---
    print("▶ Running integration tests")
    run_basic_lending(protocol, accounts)
    run_liquidation(protocol, accounts)
    run_governance_change(protocol, accounts)

    # --- Simulation engine ---
    engine = SimulationEngine(protocol)
    metrics = MetricsCollector()

    # --- Time machine ---
    time_machine = TimeMachine()
    time_machine.advance_blocks(BLOCKS_PER_DAY * 30)

    # --- Stress test ---
    simulate_billion_users(engine, metrics)

    # --- Audit assertions ---
    print("🔍 Running audit assertions")
    audit_oracle_sanity(metrics)
    audit_circuit_breaker(metrics)
    audit_treasury_growth(metrics)
    audit_governance_delay(metrics)

    # --- Export metrics ---
    with open("e2e_metrics.json", "w") as f:
        json.dump(metrics.export(), f, indent=2)

    # --- Charts ---
    plot_metrics(metrics)

    print("\n✅ ALL E2E + AUDIT TESTS PASSED")


if __name__ == "__main__":
    main()
