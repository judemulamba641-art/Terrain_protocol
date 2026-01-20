"""
Keeper Bot
----------
Automates protocol maintenance:
- interest updates
- health factor checks
- liquidation triggers
- oracle refresh
"""

import time
from web3 import Web3
from settings import (
    RPC_URL,
    BOT_ADDRESS,
    BOT_PRIVATE_KEY,
    LENDING_POOL,
    LIQUIDATION_MANAGER,
    CHECK_INTERVAL,
    ENABLE_LIQUIDATION,
    DRY_RUN,
    MAX_GAS_LIMIT
)
from sync import full_sync

# -------------------------------------------------
# WEB3
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABI PLACEHOLDERS
# -------------------------------------------------

LENDING_POOL_ABI = []          # updateInterest()
LIQUIDATION_MANAGER_ABI = []  # liquidate()

# -------------------------------------------------
# CONTRACTS
# -------------------------------------------------

lending_pool = w3.eth.contract(
    address=LENDING_POOL,
    abi=LENDING_POOL_ABI
)

liquidation_manager = w3.eth.contract(
    address=LIQUIDATION_MANAGER,
    abi=LIQUIDATION_MANAGER_ABI
)

# -------------------------------------------------
# TX HELPER
# -------------------------------------------------

def send_tx(tx):
    if DRY_RUN:
        print("[🧪 DRY-RUN] Transaction skipped")
        return None

    tx.update({
        "from": BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(BOT_ADDRESS),
        "gas": MAX_GAS_LIMIT,
        "gasPrice": w3.eth.gas_price,
    })

    signed = w3.eth.account.sign_transaction(tx, BOT_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"[📤 TX] {tx_hash.hex()}")
    return tx_hash

# -------------------------------------------------
# KEEPER LOGIC
# -------------------------------------------------

def update_interest_rates():
    print("[⏱️] Updating interest rates")
    tx = lending_pool.functions.updateInterest().build_transaction({})
    send_tx(tx)


def process_liquidations():
    print("[🔥] Checking liquidations")

    positions = full_sync()

    for p in positions:
        if p["health_factor"] < 1 and ENABLE_LIQUIDATION:
            print(f"[⚠️] Liquidating NFT {p['tokenId']}")
            tx = liquidation_manager.functions.liquidate(
                p["tokenId"]
            ).build_transaction({})
            send_tx(tx)

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def run():
    print("[🤖] Keeper started")

    while True:
        try:
            update_interest_rates()
            process_liquidations()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"[❌] Keeper error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    run()