"""
Liquidation scenario
--------------------

Scénario fonctionnel de liquidation.
Valide que le protocole protège la liquidité
lorsqu'une position devient sous-collatéralisée.
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_health_factor_below_one,
    assert_no_bad_debt,
)

from tests.integration.assertions.security_checks import (
    assert_liquidation_not_self,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
    invariant_post_liquidation_cleanup,
)


# ============================================================
# Liquidation scenario
# ============================================================

def test_scenario_liquidation(
    accounts,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock
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
    stablecoin = protocol["stablecoin"]
    land_nft = protocol["land_nft"]
    oracle = protocol["oracle"]
    nft_manager = protocol["nft_manager"]

    # ------------------
    # Lender provides liquidity
    # ------------------
    stablecoin.mint(
        acc.lender,
        800_000 * 10**18,
        {"from": acc.admin}
    )

    stablecoin.approve(
        lending_pool.address,
        800_000 * 10**18,
        {"from": acc.lender}
    )

    lending_pool.deposit(
        800_000 * 10**18,
        {"from": acc.lender}
    )

    # ------------------
    # Borrower opens position
    # ------------------
    land_nft.mint(
        acc.borrower,
        token_id=7,
        {"from": acc.admin}
    )

    oracle.setNFTPrice(
        land_nft.address,
        7,
        100_000 * 10**18,
        {"from": acc.keeper}
    )

    land_nft.approve(
        lending_pool.address,
        7,
        {"from": acc.borrower}
    )

    lending_pool.depositNFT(
        land_nft.address,
        7,
        {"from": acc.borrower}
    )

    lending_pool.borrow(
        70_000 * 10**18,
        {"from": acc.borrower}
    )

    # ------------------
    # Market shock (price drop)
    # ------------------
    oracle.setNFTPrice(
        land_nft.address,
        7,
        60_000 * 10**18,
        {"from": acc.keeper}
    )

    assert_health_factor_below_one(
        lending_pool,
        acc.borrower
    )

    # ------------------
    # Liquidation by third party
    # ------------------
    assert_liquidation_not_self(
        acc.borrower,
        acc.liquidator
    )

    lending_pool.liquidate(
        acc.borrower,
        land_nft.address,
        7,
        {"from": acc.liquidator}
    )

    # ------------------
    # Post-liquidation expectations
    # ------------------
    assert_no_bad_debt(
        lending_pool,
        acc.borrower
    )

    invariant_post_liquidation_cleanup(
        lending_pool,
        nft_manager,
        acc.borrower,
        land_nft.address,
        7
    )

    invariant_pool_solvent(
        lending_pool
    )

    assert land_nft.ownerOf(7) == acc.liquidator