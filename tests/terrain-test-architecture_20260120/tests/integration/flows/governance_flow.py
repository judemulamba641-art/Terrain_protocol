"""
Governance integration flow
---------------------------

Flow d'intégration couvrant :
- création de proposition
- vote
- timelock
- exécution
- vérifications de sécurité post-exécution

Ce flow simule un vrai cycle DAO (Aave-like).
"""

import pytest
import time

from tests.integration.assertions.security_checks import (
    assert_only_admin,
    assert_upgrade_not_immediate,
)

from tests.integration.assertions.economic_checks import (
    assert_parameter_change_reasonable,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
)


# ============================================================
# Governance flow
# ============================================================

def test_governance_parameter_update_flow(
    accounts,
    Governance,
    Timelock,
    LendingPool,
):
    """
    Flow :
    - Proposition : modifier liquidation bonus
    - Vote
    - Timelock
    - Exécution
    """

    admin = accounts[0]
    proposer = accounts[1]
    voter = accounts[2]

    # ------------------
    # Deploy governance
    # ------------------
    governance = Governance.deploy(
        Timelock.address,
        {"from": admin}
    )

    timelock = Timelock.deploy(
        2 * 24 * 60 * 60,  # 2 jours
        {"from": admin}
    )

    lending_pool = LendingPool.deploy(
        {"from": admin}
    )

    # ------------------
    # Read initial parameter
    # ------------------
    old_bonus = lending_pool.getLiquidationBonus()

    new_bonus = old_bonus + 100  # +1%

    assert_parameter_change_reasonable(
        old_bonus,
        new_bonus
    )

    # ------------------
    # Create proposal
    # ------------------
    proposal_id = governance.propose(
        target=lending_pool.address,
        value=0,
        signature="setLiquidationBonus(uint256)",
        calldata=new_bonus,
        description="Increase liquidation bonus by 1%",
        {"from": proposer}
    )

    # ------------------
    # Vote
    # ------------------
    governance.vote(
        proposal_id,
        True,
        {"from": voter}
    )

    governance.queue(
        proposal_id,
        {"from": admin}
    )

    # ------------------
    # Timelock enforcement
    # ------------------
    eta = governance.getProposalEta(proposal_id)
    now = int(time.time())

    assert_upgrade_not_immediate(
        eta,
        now
    )

    # Fast-forward time (test environment)
    chain.sleep(eta - now + 1)
    chain.mine(1)

    # ------------------
    # Execute proposal
    # ------------------
    governance.execute(
        proposal_id,
        {"from": admin}
    )

    # ------------------
    # Post execution checks
    # ------------------
    updated_bonus = lending_pool.getLiquidationBonus()

    assert updated_bonus == new_bonus, "Governance execution failed"

    invariant_pool_solvent(lending_pool)