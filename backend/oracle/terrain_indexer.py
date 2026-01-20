"""
Terrain Indexer
---------------
Indexes all 3D terrain NFTs used in the protocol
Produces a normalized off-chain state for bots & analytics
"""

import time
from web3 import Web3
from settings import (
    RPC_URL,
    TERRAIN_NFT,
    NFT_COLLATERAL_MANAGER,
    LENDING_POOL,
    PRICE_ORACLE,
    NFT_START_ID,
    NFT_MAX_ID,
)

# -------------------------------------------------
# WEB3
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABI PLACEHOLDERS
# -------------------------------------------------

ERC721_ABI = []                # ownerOf()
NFT_MANAGER_ABI = []           # isCollateral(), ownerOfCollateral()
LENDING_POOL_ABI = []          # getNFTDebt()
ORACLE_ABI = []                # getNFTPrice(), getNFTFloorPrice()

# -------------------------------------------------
# CONTRACTS
# -------------------------------------------------

terrain_nft = w3.eth.contract(
    address=TERRAIN_NFT,
    abi=ERC721_ABI
)

nft_manager = w3.eth.contract(
    address=NFT_COLLATERAL_MANAGER,
    abi=NFT_MANAGER_ABI
)

lending_pool = w3.eth.contract(
    address=LENDING_POOL,
    abi=LENDING_POOL_ABI
)

oracle = w3.eth.contract(
    address=PRICE_ORACLE,
    abi=ORACLE_ABI
)

# -------------------------------------------------
# INDEXER CORE
# -------------------------------------------------

def index_terrain(token_id: int) -> dict | None:
    """
    Index a single terrain NFT
    """
    try:
        owner = terrain_nft.functions.ownerOf(token_id).call()
        is_collateral = nft_manager.functions.isCollateral(token_id).call()

        debt = 0
        collateral_owner = None

        if is_collateral:
            collateral_owner = nft_manager.functions.ownerOfCollateral(
                token_id
            ).call()
            debt = lending_pool.functions.getNFTDebt(token_id).call()

        price = oracle.functions.getNFTPrice(
            TERRAIN_NFT,
            token_id
        ).call()

        hf = float("inf")
        if debt > 0:
            hf = price / debt

        return {
            "token_id": token_id,
            "owner": owner,
            "is_collateral": is_collateral,
            "collateral_owner": collateral_owner,
            "debt": debt,
            "price": price,
            "health_factor": hf,
            "status": (
                "LIQUIDATABLE" if hf < 1 else "SAFE"
                if is_collateral else "IDLE"
            ),
        }

    except Exception as e:
        print(f"[⚠️] Token {token_id} indexing error: {e}")
        return None


def full_index():
    """
    Index all terrain NFTs
    """
    print("[🗺️] Starting terrain indexing")

    terrains = []

    for token_id in range(NFT_START_ID, NFT_MAX_ID):
        data = index_terrain(token_id)
        if data:
            terrains.append(data)

    print(f"[✅] Indexed {len(terrains)} terrains")
    return terrains


# -------------------------------------------------
# REPORT
# -------------------------------------------------

def print_summary(terrains):
    liquidatable = [t for t in terrains if t["status"] == "LIQUIDATABLE"]

    print("\n📊 TERRAIN SUMMARY")
    print(f"Total terrains indexed: {len(terrains)}")
    print(f"Used as collateral: {len([t for t in terrains if t['is_collateral']])}")
    print(f"Liquidatable terrains: {len(liquidatable)}")

    for t in liquidatable:
        print(
            f"[🔥] NFT {t['token_id']} | "
            f"HF={t['health_factor']:.2f} | "
            f"Debt={t['debt']}"
        )


# -------------------------------------------------
# MAIN
# -------------------------------------------------

if __name__ == "__main__":
    while True:
        try:
            terrains = full_index()
            print_summary(terrains)
            time.sleep(300)  # every 5 minutes
        except Exception as e:
            print(f"[❌] Indexer error: {e}")
            time.sleep(30)