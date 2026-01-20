"""
Liquidation Bot for NFT-backed Lending Protocol
-----------------------------------------------
- Monitors NFT collateral positions
- Checks health factor via oracle & lending pool
- Triggers liquidation when under threshold

Requirements:
- web3.py
- python-dotenv
"""

import time
import os
from web3 import Web3
from dotenv import load_dotenv

# -------------------------------------------------
# ENVIRONMENT
# -------------------------------------------------

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
BOT_ADDRESS = os.getenv("BOT_ADDRESS")

LENDING_POOL = os.getenv("LENDING_POOL")
LIQUIDATION_MANAGER = os.getenv("LIQUIDATION_MANAGER")
NFT_COLLATERAL_MANAGER = os.getenv("NFT_COLLATERAL_MANAGER")
ORACLE = os.getenv("PRICE_ORACLE")

CHECK_INTERVAL = 30  # seconds
LIQUIDATION_THRESHOLD_WAD = 1e18  # HF < 1 => liquidatable

# -------------------------------------------------
# WEB3 SETUP
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC not connected"

account = w3.eth.account.from_key(PRIVATE_KEY)

# -------------------------------------------------
# ABI PLACEHOLDERS (replace with real ABIs)
# -------------------------------------------------

LENDING_POOL_ABI = []              # getUserDebt(), getNFTDebt()
NFT_MANAGER_ABI = []               # isCollateral(), ownerOfCollateral()
ORACLE_ABI = []                    # getNFTPrice()
LIQUIDATION_MANAGER_ABI = []       # liquidate()

lending_pool = w3.eth.contract(
    address=LENDING_POOL,
    abi=LENDING_POOL_ABI
)

nft_manager = w3.eth.contract(
    address=NFT_COLLATERAL_MANAGER,
    abi=NFT_MANAGER_ABI
)

oracle = w3.eth.contract(
    address=ORACLE,
    abi=ORACLE_ABI
)

liquidation_manager = w3.eth.contract(
    address=LIQUIDATION_MANAGER,
    abi=LIQUIDATION_MANAGER_ABI
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def get_health_factor(token_id: int) -> float:
    """
    HF = collateral_value / debt
    """
    owner = nft_manager.functions.ownerOfCollateral(token_id).call()
    if owner == "0x0000000000000000000000000000000000000000":
        return float("inf")

    debt = lending_pool.functions.getNFTDebt(token_id).call()
    if debt == 0:
        return float("inf")

    price = oracle.functions.getNFTPrice(
        NFT_COLLATERAL_MANAGER,
        token_id
    ).call()

    return price / debt


def liquidate(token_id: int):
    """
    Calls liquidation manager
    """
    nonce = w3.eth.get_transaction_count(BOT_ADDRESS)

    tx = liquidation_manager.functions.liquidate(
        token_id
    ).build_transaction({
        "from": BOT_ADDRESS,
        "nonce": nonce,
        "gas": 600_000,
        "gasPrice": w3.eth.gas_price
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

    print(f"[🔥] Liquidation sent for tokenId {token_id}: {tx_hash.hex()}")


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def run():
    print("[🤖] Liquidation bot started")

    token_id = 0  # example start
    MAX_TOKEN_ID = 10_000  # adapt to NFT supply

    while True:
        try:
            for token_id in range(MAX_TOKEN_ID):
                if not nft_manager.functions.isCollateral(token_id).call():
                    continue

                hf = get_health_factor(token_id)

                if hf < 1:
                    print(f"[⚠️] Liquidatable NFT {token_id} | HF={hf:.2f}")
                    liquidate(token_id)

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"[❌] Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    run()