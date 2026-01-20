"""
State Synchronizer for DeFi Terrain Protocol
-------------------------------------------
Rebuilds protocol state from on-chain data
Useful for cold start, audits, analytics, bots recovery
"""

import time
from web3 import Web3
from settings import (
    RPC_URL,
    LENDING_POOL,
    NFT_COLLATERAL_MANAGER,
    LIQUIDATION_MANAGER,
    PRICE_ORACLE,
    NFT_START_ID,
    NFT_MAX_ID,
)

# -------------------------------------------------
# WEB3 SETUP
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABI PLACEHOLDERS (replace with real ABIs)
# -------------------------------------------------

LENDING_POOL_ABI = []            # getUserDebt(), getNFTDebt()
NFT_MANAGER_ABI = []             # isCollateral(), ownerOfCollateral()
LIQUIDATION_MANAGER_ABI = []     # view helpers (optional)
ORACLE_ABI = []                  # getNFTPrice()

# -------------------------------------------------
# CONTRACTS
# -------------------------------------------------

lending_pool = w3.eth.contract(
    address=LENDING_POOL,
    abi=LENDING_POOL_ABI
)

nft_manager = w3.eth.contract(
    address=NFT_COLLATERAL_MANAGER,
    abi=NFT_MANAGER_ABI
)

oracle = w3.eth.contract(
    address=PRICE_ORACLE,
    abi=ORACLE_ABI
)

# -------------------------------------------------
# SYNC LOGIC
# -------------------------------------------------

def sync_collateral_state():
    """
    Rebuild NFT collateral state
    """
    print("[🔄] Syncing NFT collateral state...")

    collateral = []

    for token_id in range(NFT_START_ID, NFT_MAX_ID):
        try:
            if not nft_manager.functions.isCollateral(token_id).call():
                continue

            owner = nft_manager.functions.ownerOfCollateral(token_id).call()
            price = oracle.functions.getNFTPrice(
                NFT_COLLATERAL_MANAGER,
                token_id
            ).call()

            collateral.append({
                "tokenId": token_id,
                "owner": owner,
                "price": price
            })

        except Exception as e:
            print(f"[⚠️] NFT {token_id} error: {e}")

    print(f"[✅] Collateral synced: {len(collateral)} NFTs")
    return collateral


def sync_debt_state(collateral):
    """
    Attach debt data to collateral
    """
    print("[🔄] Syncing debt state...")

    positions = []

    for item in collateral:
        token_id = item["tokenId"]

        try:
            debt = lending_pool.functions.getNFTDebt(token_id).call()

            position = {
                **item,
                "debt": debt,
                "health_factor": (
                    float(item["price"]) / debt if debt > 0 else float("inf")
                )
            }

            positions.append(position)

        except Exception as e:
            print(f"[⚠️] Debt error NFT {token_id}: {e}")

    print(f"[✅] Positions synced: {len(positions)}")
    return positions


def full_sync():
    """
    Full protocol sync
    """
    print("[🚀] Starting full sync")

    collateral = sync_collateral_state()
    positions = sync_debt_state(collateral)

    print("[📊] Summary")
    for p in positions:
        status = "LIQUIDATABLE" if p["health_factor"] < 1 else "SAFE"
        print(
            f"NFT {p['tokenId']} | "
            f"Owner {p['owner'][:6]}... | "
            f"HF={p['health_factor']:.2f} | "
            f"{status}"
        )

    return positions


# -------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------

if __name__ == "__main__":
    while True:
        try:
            full_sync()
            time.sleep(300)  # sync every 5 minutes
        except Exception as e:
            print(f"[❌] Sync error: {e}")
            time.sleep(30)