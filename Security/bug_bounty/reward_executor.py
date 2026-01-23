from rpc_client import w3, send_tx
from config import BUG_BOUNTY_REGISTRY

BUG_BOUNTY_ABI = [
    {
        "name": "claim_bounty",
        "inputs": [{"name": "proposal_id", "type": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

registry = w3.eth.contract(
    address=BUG_BOUNTY_REGISTRY,
    abi=BUG_BOUNTY_ABI
)

def execute_reward(proposal_id):
    tx = registry.functions.claim_bounty(proposal_id).build_transaction({
        "from": w3.eth.default_account,
        "gas": 300_000,
    })
    return send_tx(tx)
