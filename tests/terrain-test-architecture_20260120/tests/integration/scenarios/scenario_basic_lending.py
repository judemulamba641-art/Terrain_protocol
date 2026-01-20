"""
Basic lending scenario
----------------------

Scénario d'intégration minimal du protocole lending.
Couvre le cas nominal (happy path) sans liquidation.

Ce scénario sert de référence fonctionnelle.
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_health_factor_above_one,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
    invariant_user_debt_non_negative,
)

from tests.integration.assertions.security_checks import (
    assert_borrow_not_zero,
)


# ============================================================
# Basic lending scenario
# ============================================================

def test_scenario_basic_lending(
    accounts,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock
):
    # ------------------
    # Environment setup
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

    # ------------------
    # Lender provides liquidity
    # ------------------
    stablecoin.mint(
        acc.lender,
        300_000 * 10**18,
        {"from": acc.admin}
    )

    stablecoin.approve(
        lending_pool.address,
        300_000 * 10**18,
        {"from": acc.lender}
    )

    lending_pool.deposit(
        300_000 * 10**18,
        {"from": acc.lender}
    )

    # ------------------
    # Borrower prepares collateral
    # ------------------
    land_nft.mint(
        acc.borrower,
        token_id=1,
        {"from": acc.admin}
    )

    oracle.setNFTPrice(
        land_nft.address,
        1,
        120_000 * 10**18,
        {"from": acc.keeper}
    )

    land_nft.approve(
        lending_pool.address,
        1,
        {"from": acc.borrower}
    )

    lending_pool.depositNFT(
        land_nft.address,
        1,
        {"from": acc.borrower}
    )

    # ------------------
    # Borrow
    # ------------------
    borrow_amount = 60_000 * 10**18
    assert_borrow_not_zero(borrow_amount)

    lending_pool.borrow(
        borrow_amount,
        {"from": acc.borrower}
    )

    # ------------------
    # Assertions
    # ------------------
    assert_health_factor_above_one(
        lending_pool,
        acc.borrower
    )

    invariant_user_debt_non_negative(
        lending_pool,
        acc.borrower
    )

    invariant_pool_solvent(
        lending_pool
    )