"""
Deploy Lending Protocol Core
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

def load(name):
    with open(f"contracts/{name}.json") as f:
        return json.load(f)

LendingPool = load("lending/LendingPool")
NFTManager = load("lending/NFTCollateralManager")
LiquidationManager = load("lending/LiquidationManager")
InterestStrategy = load("lending/InterestRateStrategy")
PriceOracle = load("oracle/PriceOracle")
Timelock = load("governance/Timelock")
Governor = load("governance/Governor")

def deploy_contract(artifact, args=[]):
    contract = w3.eth.contract(
        abi=artifact["abi"],
        bytecode=artifact["bytecode"]
    )

    tx = contract.constructor(*args).build_transaction({
        "from": BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(BOT_ADDRESS),
        "gas": MAX_GAS_LIMIT,
        "gasPrice": w3.eth.gas_price,
    })

    signed = w3.eth.account.sign_transaction(tx, BOT_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"[✅] Deployed at {receipt.contractAddress}")
    return receipt.contractAddress

def deploy():
    print("[🚀] Deploying Lending Protocol")

    interest = deploy_contract(InterestStrategy)
    oracle = deploy_contract(PriceOracle)
    nft_manager = deploy_contract(NFTManager)
    lending_pool = deploy_contract(
        LendingPool,
        [nft_manager, oracle, interest]
    )
    liquidation = deploy_contract(
        LiquidationManager,
        [lending_pool, nft_manager, oracle]
    )

    timelock = deploy_contract(Timelock, [BOT_ADDRESS, 86400])
    governor = deploy_contract(Governor, [timelock])

    print("\n🎉 DEPLOYMENT COMPLETE")
    print(f"LendingPool: {lending_pool}")
    print(f"NFTManager: {nft_manager}")
    print(f"Liquidation: {liquidation}")
    print(f"Oracle: {oracle}")
    print(f"Governor: {governor}")
    print(f"Timelock: {timelock}")

if __name__ == "__main__":
    deploy()