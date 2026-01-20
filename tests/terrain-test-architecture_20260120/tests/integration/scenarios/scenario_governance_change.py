"""
Governance change scenario
--------------------------

Scénario fonctionnel de gouvernance.
Valide qu'une décision DAO modifie correctement
un paramètre critique du protocole sans casser
les invariants économiques et de sécurité.
"""

import time
import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_parameter_change_reasonable,
)

from tests.integration.assertions.security_checks import (
    assert_only_admin,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
)


# ============================================================
# Governance scenario
# ============================================================

def test_scenario_governance_parameter_change(
    accounts,
    Governance,
    Timelock,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock,
    chain,
):
    # ------------------
    # Setup environment
    # ------------------
    acc = load_accounts(accounts)

    protocol = deploy_protocol(
        deployer=acc.admin,
        LendingPool=LendingPool,
        NFTCollateralManager=NFTCollateralManager,
        LiquidationManager=LiquidationManager,
        ERC20Mock=ERC20Mock,
        NFTMock=NFTMock,
        OracleMock=OracleMock,
    )

    lending_pool = protocol["lending_pool"]

    # ------------------
    # Deploy governance stack
    # ------------------
    timelock = Timelock.deploy(
        2 * 24 * 60 * 60,  # 2 jours
        {"from": acc.admin}
    )

    governance = Governance.deploy(
        timelock.address,
        {"from": acc.admin}
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
        description="DAO: increase liquidation bonus by 1%",
        {"from": acc.borrower}
    )

    # ------------------
    # Vote & queue
    # ------------------
    governance.vote(
        proposal_id,
        True,
        {"from": acc.lender}
    )

    governance.queue(
        proposal_id,
        {"from": acc.admin}
    )

    # ------------------
    # Timelock enforcement
    # ------------------
    eta = governance.getProposalEta(proposal_id)
    now = int(time.time())

    assert eta > now, "Timelock not enforced"

    chain.sleep(eta - now + 1)
    chain.mine(1)

    # ------------------
    # Execute proposal
    # ------------------
    assert_only_admin(
        tx_sender=acc.admin,
        admin=acc.admin
    )

    governance.execute(
        proposal_id,
        {"from": acc.admin}
    )

    # ------------------
    # Post-execution checks
    # ------------------
    updated_bonus = lending_pool.getLiquidationBonus()

    assert updated_bonus == new_bonus, (
        "Governance change not applied"
    )

    invariant_pool_solvent(
        lending_pool
    )