# tests/simulations/engine/simulation_engine.py

import random


class SimulationEngine:
    """
    Moteur de simulation économique et utilisateur
    Compatible stress tests massifs
    """

    def __init__(self, scheduler, supervisor, metrics):
        self.scheduler = scheduler
        self.supervisor = supervisor
        self.metrics = metrics

    # ---------------------------------
    # USER ACTION SIMULATION
    # ---------------------------------

    def simulate_user_action(self, user_id, actions, bounded=True):
        """
        Simule une action utilisateur de manière contrôlée
        """
        action = random.choice(actions)

        if bounded:
            self.supervisor.pre_action_check(user_id, action)

        # --- Simulated protocol calls ---
        if action == "deposit_nft":
            self.metrics.inc("nft_deposits")
        elif action == "borrow":
            self.metrics.inc("borrows")
        elif action == "repay":
            self.metrics.inc("repays")
        elif action == "health_check":
            self.metrics.inc("health_checks")
        elif action == "liquidation_check":
            self.metrics.inc("liquidation_checks")

        self.supervisor.post_action_check(user_id, action)

    # ---------------------------------
    # EVENT LOOP
    # ---------------------------------

    def run_until_empty(self):
        """
        Exécute tous les événements planifiés
        """
        while self.scheduler.has_events():
            event = self.scheduler.next_event()
            event.execute()
            self.metrics.inc("events_executed")
