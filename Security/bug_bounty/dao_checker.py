from rpc_client import w3
from config import DAO_ADDRESS

DAO_ABI = [
    {
        "name": "isProposalApproved",
        "inputs": [{"name": "id", "type": "uint256"}],
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    }
]

dao = w3.eth.contract(address=DAO_ADDRESS, abi=DAO_ABI)

def is_approved(proposal_id):
    return dao.functions.isProposalApproved(proposal_id).call()
