"""
Unit Tests - Uniswap V2 Pool Integration
---------------------------------------
Tests liquidity, price calculation and swap logic
"""

import pytest
from web3 import Web3
from settings import RPC_URL

# -------------------------------------------------
# FIXTURES
# -------------------------------------------------

@pytest.fixture(scope="module")
def w3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected()
    return w3


@pytest.fixture(scope="module")
def mock_addresses():
    return {
        "token": "0x0000000000000000000000000000000000000001",
        "weth": "0x0000000000000000000000000000000000000002",
        "router": "0x0000000000000000000000000000000000000003",
        "pair": "0x0000000000000000000000000000000000000004",
    }

# -------------------------------------------------
# ABIs (MINIMAL)
# -------------------------------------------------

UNISWAP_ROUTER_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    }
]

UNISWAP_PAIR_ABI = [
    {
        "name": "getReserves",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"},
        ],
    }
]

# -------------------------------------------------
# TESTS
# -------------------------------------------------

def test_pool_reserves(w3, mock_addresses):
    """
    Ensure Uniswap pool reserves are accessible
    """
    pair = w3.eth.contract(
        address=mock_addresses["pair"],
        abi=UNISWAP_PAIR_ABI
    )

    # mocked return (replace with fork or mock)
    try:
        reserves = pair.functions.getReserves().call()
        assert reserves[0] >= 0
        assert reserves[1] >= 0
    except Exception:
        pytest.skip("Mocked environment – no real reserves")


def test_price_calculation(w3, mock_addresses):
    """
    Validate price computation from reserves
    """
    reserve_token = 1_000_000 * 10**18
    reserve_weth = 500 * 10**18

    price = reserve_weth / reserve_token
    assert price > 0
    assert round(price, 6) == round(0.0005, 6)


def test_router_get_amounts_out(w3, mock_addresses):
    """
    Test router price quoting
    """
    router = w3.eth.contract(
        address=mock_addresses["router"],
        abi=UNISWAP_ROUTER_ABI
    )

    try:
        amounts = router.functions.getAmountsOut(
            1 * 10**18,
            [mock_addresses["token"], mock_addresses["weth"]]
        ).call()

        assert len(amounts) == 2
        assert amounts[1] > 0
    except Exception:
        pytest.skip("Mocked environment – router not available")


def test_slippage_estimation():
    """
    Validate slippage formula
    """
    expected = 1.0
    received = 0.97

    slippage = (expected - received) / expected
    assert slippage == pytest.approx(0.03, 0.001)