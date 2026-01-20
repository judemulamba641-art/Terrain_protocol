"""
Market crash scenario
---------------------

Scénario de stress test systémique.
Simule un crash brutal du prix des NFT collatéraux
et vérifie la résilience globale du protocole.
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_health_factor_below_one,
    assert_no_bad_debt,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_pool_solvent,
)

from tests.integration.assertions.security_checks import (
    assert_liquidation_not_self,
)


# ============================================================
# Market crash scenario
# ============================================================

def test_scenario_market_crash(
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

    # ------------------
    # Liquidity providers
    # ------------------
    stablecoin.mint(
        acc.lender,
        1_500_000 * 10**18,
        {"from": acc.admin}
    )

    stablecoin.approve(
        lending_pool.address,
        1_500_000 * 10**18,
        {"from": acc.lender}
    )

    lending_pool.deposit(
        1_500_000 * 10**18,
        {"from": acc.lender}
    )

    # ------------------
    # Multiple borrowers open positions
    # ------------------
    borrowers = [acc.borrower1, acc.borrower2, acc.borrower3]
    nft_ids = [11, 12, 13]
    nft_price = 120_000 * 10**18
    borrow_amount = 80_000 * 10**18

    for user, token_id in zip(borrowers, nft_ids):
        land_nft.mint(
            user,
            token_id,
            {"from": acc.admin}
        )

        oracle.setNFTPrice(
            land_nft.address,
            token_id,
            nft_price,
            {"from": acc.keeper}
        )

        land_nft.approve(
            lending_pool.address,
            token_id,
            {"from": user}
        )

        lending_pool.depositNFT(
            land_nft.address,
            token_id,
            {"from": user}
        )

        lending_pool.borrow(
            borrow_amount,
            {"from": user}
        )

    # ------------------
    # Market crash (−50%)
    # ------------------
    crash_price = nft_price // 2

    for token_id in nft_ids:
        oracle.setNFTPrice(
            land_nft.address,
            token_id,
            crash_price,
            {"from": acc.keeper}
        )

    for user in borrowers:
        assert_health_factor_below_one(
            lending_pool,
            user
        )

    # ------------------
    # Mass liquidation
    # ------------------
    for user, token_id in zip(borrowers, nft_ids):
        assert_liquidation_not_self(
            user,
            acc.liquidator
        )

        lending_pool.liquidate(
            user,
            land_nft.address,
            token_id,
            {"from": acc.liquidator}
        )

        assert_no_bad_debt(
            lending_pool,
            user
        )

    # ------------------
    # Global invariants
    # ------------------
    invariant_pool_solvent(
        lending_pool
    )

    # Optional sanity: pool balance still positive
    assert lending_pool.totalLiquidity() > 0