# tests/e2e_and_test_runner.py

import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.event_scheduler import EventScheduler
from tests.simulations.engine.time_machine import TimeMachine

from tests.simulations.metrics import MetricsCollector
from tests.simulations.reports.report_generator import ReportGenerator

from tests.supervisor import Supervisor

from tests.integration.scenarios.scenario_basic_lending import run_basic_lending
from tests.integration.scenarios.scenario_nft_borrow import run_nft_borrow
from tests.integration.scenarios.scenario_liquidation import run_liquidation
from tests.integration.scenarios.scenario_governance_change import run_governance_change
from tests.integration.scenarios.scenario_market_crash import run_market_crash

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

TOTAL_SIMULATED_USERS = 1_000_000_000  # 1 billion
SIMULATION_BATCH_SIZE = 10_000         # scalable chunk
MAX_WORKERS = 16                       # CPU bound safe
SIMULATION_DURATION = 7 * 24 * 3600    # 7 days simulated time

# ---------------------------------------------------------
# GLOBAL OBJECTS
# ---------------------------------------------------------

metrics = MetricsCollector()
supervisor = Supervisor(metrics=metrics)
time_machine = TimeMachine()
scheduler = EventScheduler(time_machine=time_machine)
engine = SimulationEngine(
    scheduler=scheduler,
    supervisor=supervisor,
    metrics=metrics
)

# ---------------------------------------------------------
# E2E TEST SUITE
# ---------------------------------------------------------

def run_e2e_core_tests():
    print("\n[ E2E ] Running core integration scenarios...\n")

    run_basic_lending(metrics)
    run_nft_borrow(metrics)
    run_liquidation(metrics)
    run_governance_change(metrics)
    run_market_crash(metrics)

    print("[ E2E ] Core scenarios completed.\n")


# ---------------------------------------------------------
# MASS USER SIMULATION (1 BILLION USERS)
# ---------------------------------------------------------

def simulate_user_batch(batch_id, batch_size):
    """
    Simulates a batch of users performing random but bounded actions.
    """
    for i in range(batch_size):
        engine.simulate_user_action(
            user_id=f"user_{batch_id}_{i}",
            actions=[
                "deposit_nft",
                "borrow",
                "repay",
                "health_check",
                "liquidation_check"
            ],
            bounded=True  # audit requirement
        )


def run_mass_user_simulation():
    print("\n[ SIMULATION ] Starting 1 billion users stress test...\n")

    total_batches = math.ceil(TOTAL_SIMULATED_USERS / SIMULATION_BATCH_SIZE)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for batch_id in range(total_batches):
            executor.submit(simulate_user_batch, batch_id, SIMULATION_BATCH_SIZE)

            if batch_id % 100 == 0:
                print(f"[ SIMULATION ] Progress: {batch_id}/{total_batches} batches")

    print("[ SIMULATION ] Mass user simulation completed.\n")


# ---------------------------------------------------------
# POST-AUDIT SAFETY TESTS (NO CONTRACT MODIFICATION)
# ---------------------------------------------------------

def run_audit_guard_tests():
    print("\n[ AUDIT ] Running post-audit guardrail tests...\n")

    supervisor.assert_oracle_sanity()
    supervisor.assert_no_infinite_mint()
    supervisor.assert_treasury_balance_consistency()
    supervisor.assert_governance_delay_respected()
    supervisor.assert_circuit_breaker_triggerable()

    print("[ AUDIT ] Guardrail tests passed.\n")


# ---------------------------------------------------------
# TIME-BASED SIMULATION
# ---------------------------------------------------------

def run_time_simulation():
    print("\n[ TIME ] Advancing simulated time...\n")

    time_machine.advance_time(SIMULATION_DURATION)
    engine.run_until_empty()

    print("[ TIME ] Time simulation completed.\n")


# ---------------------------------------------------------
# FINAL REPORTING
# ---------------------------------------------------------

def generate_reports():
    print("\n[ REPORT ] Generating metrics and reports...\n")

    report = ReportGenerator(metrics)
    report.generate_json("reports/e2e_metrics.json")
    report.generate_csv("reports/e2e_metrics.csv")
    report.generate_graphs()  # matplotlib hooks

    print("[ REPORT ] Reports generated.\n")


# ---------------------------------------------------------
# MAIN RUNNER
# ---------------------------------------------------------

def main():
    start = time.time()

    print("\n==============================")
    print("  E2E PROTOCOL TEST RUNNER")
    print("==============================\n")

    run_e2e_core_tests()
    run_audit_guard_tests()
    run_mass_user_simulation()
    run_time_simulation()
    generate_reports()

    elapsed = time.time() - start
    print(f"\n✅ ALL TESTS COMPLETED IN {elapsed:.2f}s\n")


if __name__ == "__main__":
    main()
