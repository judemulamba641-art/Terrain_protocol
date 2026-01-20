"""
Liquidation integration flow
----------------------------

Flow critique couvrant :
- position sous-collatéralisée
- déclenchement de liquidation
- transfert du NFT
- nettoyage de la dette
- invariants post-liquidation
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
    invariant_post_liquidation_cleanup,
    invariant_pool_solvent,
)


# ============================================================
# Liquidation flow
# ============================================================

def test_liquidation_flow(
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
    nft_manager = protocol["nft_manager"]

    # ------------------
    # Provide liquidity
    # ------------------
    stablecoin.mint(
        acc.lender,
        1_000_000 * 10**18,
        {"from": acc.admin}
    )

    stablecoin.approve(
        lending_pool.address,
        1_000_000 * 10**18,
        {"from": acc.lender}
    )

    lending_pool.deposit(
        1_000_000 * 10**18,
        {"from": acc.lender}
    )

    # ------------------
    # Mint & collateralize NFT
    # ------------------
    land_nft.mint(acc.borrower, 42, {"from": acc.admin})

    oracle.setNFTPrice(
        land_nft.address,
        42,
        100_000 * 10**18,
        {"from": acc.keeper}
    )

    land_nft.approve(
        lending_pool.address,
        42,
        {"from": acc.borrower}
    )

    lending_pool.depositNFT(
        land_nft.address,
        42,
        {"from": acc.borrower}
    )

    # ------------------
    # Borrow close to max LTV
    # ------------------
    lending_pool.borrow(
        74_000 * 10**18,  # proche du threshold 75%
        {"from": acc.borrower}
    )

    # ------------------
    # Price drop → unhealthy
    # ------------------
    oracle.setNFTPrice(
        land_nft.address,
        42,
        65_000 * 10**18,
        {"from": acc.keeper}
    )

    assert_health_factor_below_one(
        lending_pool,
        acc.borrower
    )

    # ------------------
    # Liquidation
    # ------------------
    assert_liquidation_not_self(
        acc.borrower,
        acc.liquidator
    )

    lending_pool.liquidate(
        acc.borrower,
        land_nft.address,
        42,
        {"from": acc.liquidator}
    )

    # ------------------
    # Post-liquidation checks
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
        42
    )

    invariant_pool_solvent(
        lending_pool
    )

    assert land_nft.ownerOf(42) == acc.liquidator