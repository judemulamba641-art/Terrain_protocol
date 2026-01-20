"""
Uniswap integration flow
------------------------

Flow d'intégration couvrant :
- création de liquidité Uniswap
- pricing on-chain
- interaction avec le protocole DeFi
- invariants post-AMM

Ce test simule un setup token réel (launch + liquidity).
"""

import pytest

from tests.integration.environment.accounts import load_accounts
from tests.integration.environment.deploy_protocol import deploy_protocol

from tests.integration.assertions.economic_checks import (
    assert_pool_solvency,
)

from tests.integration.assertions.protocol_invariant import (
    invariant_oracle_price_positive,
)

from tests.integration.assertions.security_checks import (
    assert_not_zero_address,
)


# ============================================================
# Uniswap flow
# ============================================================

def test_uniswap_liquidity_flow(
    accounts,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock,
    UniswapV2Factory,
    UniswapV2Router02,
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

    stablecoin = protocol["stablecoin"]
    protocol_token = protocol["protocol_token"]
    oracle = protocol["oracle"]
    lending_pool = protocol["lending_pool"]

    # ------------------
    # Deploy Uniswap
    # ------------------
    factory = UniswapV2Factory.deploy(
        acc.admin,
        {"from": acc.admin}
    )

    router = UniswapV2Router02.deploy(
        factory.address,
        stablecoin.address,
        {"from": acc.admin}
    )

    # ------------------
    # Mint tokens
    # ------------------
    stablecoin.mint(
        acc.admin,
        1_000_000 * 10**18,
        {"from": acc.admin}
    )

    protocol_token.mint(
        acc.admin,
        1_000_000 * 10**18,
        {"from": acc.admin}
    )

    # ------------------
    # Approvals
    # ------------------
    stablecoin.approve(
        router.address,
        500_000 * 10**18,
        {"from": acc.admin}
    )

    protocol_token.approve(
        router.address,
        500_000 * 10**18,
        {"from": acc.admin}
    )

    # ------------------
    # Add liquidity
    # ------------------
    router.addLiquidity(
        protocol_token.address,
        stablecoin.address,
        500_000 * 10**18,
        500_000 * 10**18,
        0,
        0,
        acc.treasury,
        2**256 - 1,
        {"from": acc.admin}
    )

    pair_address = factory.getPair(
        protocol_token.address,
        stablecoin.address
    )

    assert_not_zero_address(pair_address)

    # ------------------
    # Read price from pool
    # ------------------
    pair = UniswapV2Pair.at(pair_address)

    reserves = pair.getReserves()
    reserve_token = reserves[0]
    reserve_stable = reserves[1]

    price = reserve_stable * 10**18 // reserve_token

    invariant_oracle_price_positive(
        oracle,
        protocol_token.address
    )

    # ------------------
    # Push price to oracle
    # ------------------
    oracle.setPrice(
        protocol_token.address,
        price,
        {"from": acc.keeper}
    )

    # ------------------
    # Final invariants
    # ------------------
    total_liquidity = lending_pool.getAvailableLiquidity()
    total_debt = lending_pool.getTotalDebt()

    assert_pool_solvency(
        total_liquidity,
        total_debt
    )