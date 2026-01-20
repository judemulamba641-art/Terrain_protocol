"""
Lending integration flow
------------------------

Flow principal du protocole lending / borrowing.
Couvre le cycle complet :
- deposit
- collateralize NFT
- borrow
- repay
- withdraw

Ce flow représente le happy path standard.
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_health_factor_above_one,
)

from tests.integration.assertions.security_checks import (
    assert_borrow_not_zero,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
    invariant_user_debt_non_negative,
)


# ============================================================
# Lending flow
# ============================================================

def test_lending_happy_path(
    accounts,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock
):
    # ------------------
    # Setup
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
    # Provide liquidity
    # ------------------
    stablecoin.mint(
        acc.lender,
        500_000 * 10**18,
        {"from": acc.admin}
    )

    stablecoin.approve(
        lending_pool.address,
        500_000 * 10**18,
        {"from": acc.lender}
    )

    lending_pool.deposit(
        500_000 * 10**18,
        {"from": acc.lender}
    )

    # ------------------
    # Mint & price NFT
    # ------------------
    land_nft.mint(acc.borrower, 1, {"from": acc.admin})

    oracle.setNFTPrice(
        land_nft.address,
        1,
        100_000 * 10**18,
        {"from": acc.keeper}
    )

    # ------------------
    # Deposit NFT as collateral
    # ------------------
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
    borrow_amount = 50_000 * 10**18
    assert_borrow_not_zero(borrow_amount)

    lending_pool.borrow(
        borrow_amount,
        {"from": acc.borrower}
    )

    assert_health_factor_above_one(
        lending_pool,
        acc.borrower
    )

    invariant_user_debt_non_negative(
        lending_pool,
        acc.borrower
    )

    # ------------------
    # Repay
    # ------------------
    stablecoin.approve(
        lending_pool.address,
        borrow_amount,
        {"from": acc.borrower}
    )

    lending_pool.repay(
        borrow_amount,
        {"from": acc.borrower}
    )

    invariant_user_debt_non_negative(
        lending_pool,
        acc.borrower
    )

    # ------------------
    # Withdraw collateral
    # ------------------
    lending_pool.withdrawNFT(
        land_nft.address,
        1,
        {"from": acc.borrower}
    )

    # ------------------
    # Final invariants
    # ------------------
    invariant_pool_solvent(lending_pool)