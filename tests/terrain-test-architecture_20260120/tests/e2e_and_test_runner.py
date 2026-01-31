# tests/e2e_and_test_runner.py

import math
from concurrent.futures import ThreadPoolExecutor

from tests.simulations.engine.simulation_engine import SimulationEngine
from tests.simulations.engine.event_scheduler import EventScheduler
from tests.simulations.engine.time_machine import TimeMachine
from tests.simulations.metrics import MetricsCollector
from tests.supervisor import Supervisor

# Visualization
from visualization.terrain_generator import generate_terrain_grid
from visualization.terrain_metrics import compute_health_factor
from visualization.terrain_viewer import plot_terrain_map

# Integration scenarios
from tests.integration.scenarios.scenario_basic_lending import run_basic_lending
from tests.integration.scenarios.scenario_nft_borrow import run_nft_borrow
from tests.integration.scenarios.scenario_liquidation import run_liquidation
from tests.integration.scenarios.scenario_governance_change import run_governance_change
from tests.integration.scenarios.scenario_market_crash import run_market_crash


TOTAL_USERS = 1_000_000_000
BATCH_SIZE = 10_000
MAX_WORKERS = 16


def main():
    metrics = MetricsCollector()
    supervisor = Supervisor(metrics)
    time_machine = TimeMachine()
    scheduler = EventScheduler(time_machine)

    engine = SimulationEngine(
        scheduler=scheduler,
        supervisor=supervisor,
        metrics=metrics
    )

    # -----------------------------
    # CORE E2E TESTS
    # -----------------------------
    run_basic_lending(metrics)
    run_nft_borrow(metrics)
    run_liquidation(metrics)
    run_governance_change(metrics)
    run_market_crash(metrics)

    metrics.snapshot("core_e2e_completed")

    # -----------------------------
    # MASS USER SIMULATION
    # -----------------------------

    def simulate_batch(batch_id):
        for i in range(BATCH_SIZE):
            engine.simulate_user_action(
                user_id=f"user_{batch_id}_{i}",
                actions=[
                    "deposit_nft",
                    "borrow",
                    "repay",
                    "health_check",
                    "liquidation_check"
                ],
                bounded=True
            )

    total_batches = math.ceil(TOTAL_USERS / BATCH_SIZE)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for batch_id in range(total_batches):
            executor.submit(simulate_batch, batch_id)

    metrics.snapshot("mass_user_simulation_done")

    # -----------------------------
    # TERRAIN MAP SIMULATION
    # -----------------------------
    x, y, z = generate_terrain_grid()
    hf = compute_health_factor(z)

    metrics.record_terrain_map(z, hf)

    plot_terrain_map()

    # -----------------------------
    # FINAL EXPORT
    # -----------------------------
    report = metrics.export()
    print("\nFINAL METRICS SUMMARY\n", report)


if __name__ == "__main__":
    main()
