"""
Deploy Terrain NFT (ERC721)
"""

from web3 import Web3
from settings import (
    RPC_URL,
    BOT_PRIVATE_KEY,
    BOT_ADDRESS,
    MAX_GAS_LIMIT
)
import json

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected()

with open("contracts/nft/TerrainNFT.json") as f:
    artifact = json.load(f)

abi = artifact["abi"]
bytecode = artifact["bytecode"]

def deploy():
    nft = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx = nft.constructor(
        "Terrain 3D",
        "LAND3D"
    ).build_transaction({
        "from": BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(BOT_ADDRESS),
        "gas": MAX_GAS_LIMIT,
        "gasPrice": w3.eth.gas_price,
    })

    signed = w3.eth.account.sign_transaction(tx, BOT_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[✅] NFT deployed at {receipt.contractAddress}")

if __name__ == "__main__":
    deploy()