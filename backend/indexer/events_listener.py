"""
Event Listener for DeFi Terrain Protocol
---------------------------------------
Listens to on-chain events and reacts in real time
"""

import time
from web3 import Web3
from settings import (
    RPC_URL,
    LENDING_POOL,
    NFT_COLLATERAL_MANAGER,
    LIQUIDATION_MANAGER,
    GOVERNOR,
    CHECK_INTERVAL
)

# -------------------------------------------------
# WEB3 SETUP
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC connection failed"

# -------------------------------------------------
# ABI PLACEHOLDERS (replace with real ABIs)
# -------------------------------------------------

LENDING_POOL_ABI = []              # Borrowed, Repaid
NFT_MANAGER_ABI = []               # CollateralDeposited, Withdrawn
LIQUIDATION_MANAGER_ABI = []       # Liquidated
GOVERNOR_ABI = []                  # ProposalCreated, Executed

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

liquidation_manager = w3.eth.contract(
    address=LIQUIDATION_MANAGER,
    abi=LIQUIDATION_MANAGER_ABI
)

governor = (
    w3.eth.contract(address=GOVERNOR, abi=GOVERNOR_ABI)
    if GOVERNOR
    else None
)

# -------------------------------------------------
# EVENT HANDLERS
# -------------------------------------------------

def on_borrow(event):
    args = event["args"]
    print(
        f"[📉 BORROW] user={args['user']} "
        f"amount={args['amount']} "
        f"tokenId={args['tokenId']}"
    )


def on_repay(event):
    args = event["args"]
    print(
        f"[💰 REPAY] user={args['user']} "
        f"amount={args['amount']}"
    )


def on_collateral_deposit(event):
    args = event["args"]
    print(
        f"[🏞️ COLLATERAL DEPOSIT] "
        f"user={args['user']} tokenId={args['tokenId']}"
    )


def on_collateral_withdraw(event):
    args = event["args"]
    print(
        f"[🏞️ COLLATERAL WITHDRAW] "
        f"user={args['user']} tokenId={args['tokenId']}"
    )


def on_liquidation(event):
    args = event["args"]
    print(
        f"[🔥 LIQUIDATION] "
        f"user={args['user']} "
        f"liquidator={args['liquidator']} "
        f"tokenId={args['tokenId']}"
    )


def on_proposal_created(event):
    args = event["args"]
    print(
        f"[🗳️ PROPOSAL CREATED] "
        f"id={args['proposalId']} proposer={args['proposer']}"
    )


def on_proposal_executed(event):
    args = event["args"]
    print(
        f"[✅ PROPOSAL EXECUTED] id={args['proposalId']}"
    )

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def run():
    print("[👂] Event listener started")

    last_block = w3.eth.block_number

    while True:
        try:
            latest = w3.eth.block_number

            if latest > last_block:
                from_block = last_block + 1
                to_block = latest

                # LendingPool
                for event in lending_pool.events.Borrowed().get_logs(
                    fromBlock=from_block, toBlock=to_block
                ):
                    on_borrow(event)

                for event in lending_pool.events.Repaid().get_logs(
                    fromBlock=from_block, toBlock=to_block
                ):
                    on_repay(event)

                # NFT Collateral
                for event in nft_manager.events.CollateralDeposited().get_logs(
                    fromBlock=from_block, toBlock=to_block
                ):
                    on_collateral_deposit(event)

                for event in nft_manager.events.CollateralWithdrawn().get_logs(
                    fromBlock=from_block, toBlock=to_block
                ):
                    on_collateral_withdraw(event)

                # Liquidation
                for event in liquidation_manager.events.CollateralSeized().get_logs(
                    fromBlock=from_block, toBlock=to_block
                ):
                    on_liquidation(event)

                # Governance
                if governor:
                    for event in governor.events.ProposalCreated().get_logs(
                        fromBlock=from_block, toBlock=to_block
                    ):
                        on_proposal_created(event)

                    for event in governor.events.ProposalExecuted().get_logs(
                        fromBlock=from_block, toBlock=to_block
                    ):
                        on_proposal_executed(event)

                last_block = latest

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"[❌] Listener error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()