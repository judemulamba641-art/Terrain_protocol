"""
Price Engine
------------
Off-chain pricing engine:
- NFT pricing
- token pricing
- TWAP / fallback logic
- feeds on-chain oracle
"""

import time
from web3 import Web3
from statistics import median
from settings import (
    RPC_URL,
    PRICE_ORACLE,
    UNISWAP_ROUTER,
    TERRAIN_NFT,
    CHECK_INTERVAL
)

# -------------------------------------------------
# WEB3
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABI PLACEHOLDERS
# -------------------------------------------------

ORACLE_ABI = []          # setNFTPrice(), setAssetPrice()
UNISWAP_ROUTER_ABI = []  # getAmountsOut()

# -------------------------------------------------
# CONTRACTS
# -------------------------------------------------

oracle = w3.eth.contract(
    address=PRICE_ORACLE,
    abi=ORACLE_ABI
)

router = w3.eth.contract(
    address=UNISWAP_ROUTER,
    abi=UNISWAP_ROUTER_ABI
)

# -------------------------------------------------
# PRICE SOURCES (STUBS)
# -------------------------------------------------

def fetch_marketplace_prices():
    """
    Fetch NFT prices from marketplace API
    """
    # Placeholder – replace with real API
    return [1_000e18, 1_050e18, 980e18]


def fetch_uniswap_price(token_in, token_out):
    """
    Fetch token price via Uniswap
    """
    try:
        amounts = router.functions.getAmountsOut(
            1_000_000_000_000_000_000,
            [token_in, token_out]
        ).call()
        return amounts[-1]
    except Exception:
        return None

# -------------------------------------------------
# ENGINE LOGIC
# -------------------------------------------------

def compute_nft_floor_price():
    prices = fetch_marketplace_prices()
    return int(median(prices))


def push_prices():
    print("[📈] Updating oracle prices")

    nft_price = compute_nft_floor_price()

    tx = oracle.functions.setNFTFloorPrice(
        TERRAIN_NFT,
        nft_price
    ).build_transaction({})

    print(f"[🏞️] NFT floor price = {nft_price}")

    # TX signing intentionally omitted
    # Should be pushed by DAO / Keeper wallet

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def run():
    print("[🧮] Price engine started")

    while True:
        try:
            push_prices()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"[❌] Price engine error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    run()