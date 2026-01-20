"""
NFT borrow scenario
-------------------

Scénario fonctionnel nominal :
un utilisateur dépose un NFT terrain 3D
comme collatéral et emprunte des fonds.
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_health_factor_above_one,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_nft_registered,
    invariant_pool_solvent,
)


# ============================================================
# NFT borrow scenario
# ============================================================

def test_scenario_nft_borrow(
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
    # Borrower deposits NFT
    # ------------------
    token_id = 21

    land_nft.mint(
        acc.borrower,
        token_id,
        {"from": acc.admin}
    )

    oracle.setNFTPrice(
        land_nft.address,
        token_id,
        120_000 * 10**18,
        {"from": acc.keeper}
    )

    land_nft.approve(
        lending_pool.address,
        token_id,
        {"from": acc.borrower}
    )

    lending_pool.depositNFT(
        land_nft.address,
        token_id,
        {"from": acc.borrower}
    )

    # ------------------
    # Borrow against NFT
    # ------------------
    borrow_amount = 70_000 * 10**18

    lending_pool.borrow(
        borrow_amount,
        {"from": acc.borrower}
    )

    # ------------------
    # Assertions
    # ------------------
    assert stablecoin.balanceOf(acc.borrower) == borrow_amount

    assert_health_factor_above_one(
        lending_pool,
        acc.borrower
    )

    invariant_nft_registered(
        nft_manager,
        acc.borrower,
        land_nft.address,
        token_id
    )

    invariant_pool_solvent(
        lending_pool
    )