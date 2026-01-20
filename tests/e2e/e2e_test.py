"""
End-to-End Protocol Test
========================

Test E2E complet du protocole DeFi NFT Lending :
- dépôt de liquidité
- NFT en collatéral
- borrow
- variation de prix
- liquidation
- vérification des invariants

Niveau : testnet / audit
"""

import pytest

from tests.integration.environment.deploy_protocol import deploy_protocol
from tests.integration.environment.accounts import get_test_accounts
from tests.integration.assertions.protocol_invariant import (
    assert_protocol_solvency,
    assert_no_negative_balances,
)
from tests.integration.flows.lending_flow import supply_liquidity, borrow
from tests.integration.flows.liquidation_flow import liquidate
from tests.integration.flows.uniswap_flow import provide_initial_liquidity
from tests.integration.flows.governance_flow import execute_timelock_change


# ============================================================
# E2E TEST
# ============================================================

@pytest.mark.e2e
def test_full_protocol_lifecycle():
    """
    Full end-to-end protocol test.
    """

    # --------------------------------------------------------
    # 1. Setup environment
    # --------------------------------------------------------
    accounts = get_test_accounts()

    deployer = accounts["deployer"]
    lp = accounts["liquidity_provider"]
    borrower = accounts["borrower"]
    liquidator = accounts["liquidator"]
    gov = accounts["governance"]

    protocol = deploy_protocol(deployer)

    lending_pool = protocol["lending_pool"]
    nft = protocol["nft"]
    oracle = protocol["oracle"]
    token = protocol["token"]

    # --------------------------------------------------------
    # 2. Initial liquidity (Uniswap + Pool)
    # --------------------------------------------------------
    provide_initial_liquidity(
        token=token,
        provider=lp,
        amount=1_000_000
    )

    supply_liquidity(
        pool=lending_pool,
        provider=lp,
        amount=500_000
    )

    assert lending_pool.totalLiquidity() > 0

    # --------------------------------------------------------
    # 3. NFT mint & deposit as collateral
    # --------------------------------------------------------
    nft_id = nft.mint(borrower, metadata_uri="ipfs://terrain-001")

    nft.approve(
        operator=lending_pool.address,
        token_id=nft_id,
        sender=borrower
    )

    lending_pool.depositNFTCollateral(
        borrower,
        nft.address,
        nft_id
    )

    assert lending_pool.isNFTDeposited(borrower, nft_id)

    # --------------------------------------------------------
    # 4. Borrow against NFT
    # --------------------------------------------------------
    borrow_amount = lending_pool.getMaxBorrow(borrower) * 0.7

    borrow(
        pool=lending_pool,
        borrower=borrower,
        amount=borrow_amount
    )

    hf = lending_pool.healthFactor(borrower)
    assert hf > 1

    # --------------------------------------------------------
    # 5. Oracle price drop (market stress)
    # --------------------------------------------------------
    oracle.setPrice(
        oracle.getPrice() * 0.5
    )

    hf_after = lending_pool.healthFactor(borrower)
    assert hf_after < 1

    # --------------------------------------------------------
    # 6. Liquidation
    # --------------------------------------------------------
    liquidate(
        pool=lending_pool,
        liquidator=liquidator,
        borrower=borrower
    )

    assert not lending_pool.hasOpenPosition(borrower)

    # --------------------------------------------------------
    # 7. Governance sanity (timelock path)
    # --------------------------------------------------------
    execute_timelock_change(
        protocol=protocol,
        proposer=gov,
        param="liquidation_bonus",
        new_value=1.1
    )

    assert protocol["liquidation_manager"].bonus() == 1.1

    # --------------------------------------------------------
    # 8. Global invariants
    # --------------------------------------------------------
    assert_protocol_solvency(protocol)
    assert_no_negative_balances(protocol)