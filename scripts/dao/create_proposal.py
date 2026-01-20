"""
DAO Proposal Creator
--------------------
Creates governance proposals for the DeFi Terrain Protocol
"""

from web3 import Web3
from eth_abi import encode
from settings import (
    RPC_URL,
    BOT_ADDRESS,
    BOT_PRIVATE_KEY,
    GOVERNOR,
    TIMELOCK,
    MAX_GAS_LIMIT
)

# -------------------------------------------------
# WEB3
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABIs (MINIMAL)
# -------------------------------------------------

GOVERNOR_ABI = [
    {
        "name": "propose",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "targets", "type": "address[]"},
            {"name": "values", "type": "uint256[]"},
            {"name": "calldatas", "type": "bytes[]"},
            {"name": "description", "type": "string"},
        ],
        "outputs": [{"type": "uint256"}],
    }
]

# -------------------------------------------------
# CONTRACT
# -------------------------------------------------

governor = w3.eth.contract(
    address=GOVERNOR,
    abi=GOVERNOR_ABI
)

# -------------------------------------------------
# TX HELPER
# -------------------------------------------------

def send_tx(tx):
    tx.update({
        "from": BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(BOT_ADDRESS),
        "gas": MAX_GAS_LIMIT,
        "gasPrice": w3.eth.gas_price,
    })

    signed = w3.eth.account.sign_transaction(tx, BOT_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

    print(f"[📤] Proposal TX sent: {tx_hash.hex()}")
    return tx_hash

# -------------------------------------------------
# PROPOSAL BUILDERS
# -------------------------------------------------

def build_call(target, signature, args):
    """
    Encode a function call for governance proposal
    """
    selector = w3.keccak(text=signature)[:4]
    encoded_args = encode(
        [a[0] for a in args],
        [a[1] for a in args]
    )
    return selector + encoded_args


def propose(
    targets,
    values,
    calldatas,
    description
):
    tx = governor.functions.propose(
        targets,
        values,
        calldatas,
        description
    ).build_transaction({})

    return send_tx(tx)

# -------------------------------------------------
# EXAMPLES
# -------------------------------------------------

def proposal_update_ltv(
    lending_pool,
    new_ltv: int
):
    calldata = build_call(
        target=lending_pool,
        signature="setBaseLTV(uint256)",
        args=[("uint256", new_ltv)]
    )

    return propose(
        targets=[lending_pool],
        values=[0],
        calldatas=[calldata],
        description=f"Update base LTV to {new_ltv}"
    )


def proposal_update_oracle(
    price_oracle,
    new_oracle: str
):
    calldata = build_call(
        target=price_oracle,
        signature="setOracle(address)",
        args=[("address", new_oracle)]
    )

    return propose(
        targets=[price_oracle],
        values=[0],
        calldatas=[calldata],
        description="Update price oracle"
    )

# -------------------------------------------------
# MAIN
# -------------------------------------------------

if __name__ == "__main__":
    print("[🗳️] Creating governance proposal")

    # Example usage (adjust addresses & values)
    # proposal_update_ltv(
    #     lending_pool="0xYourLendingPool",
    #     new_ltv=6000  # 60.00%
    # )

    print("Edit the script to create your proposal.")