"""
Fork setup utilities
--------------------

But :
- Démarrer un fork mainnet/testnet de manière déterministe
- Centraliser la configuration fork
- Être utilisable par les tests d'intégration ET de simulation

Compatible :
- Brownie
- Ape
- Anvil / Hardhat fork
"""

import os


# ============================================================
# Fork configuration
# ============================================================

FORK_ENABLED = os.getenv("FORK_ENABLED", "false").lower() == "true"

FORK_NETWORK = os.getenv("FORK_NETWORK", "mainnet")  # mainnet | sepolia | arbitrum
FORK_BLOCK = int(os.getenv("FORK_BLOCK", "19000000"))

# RPC URLs (jamais hardcodés)
RPC_URLS = {
    "mainnet": os.getenv("MAINNET_RPC_URL"),
    "sepolia": os.getenv("SEPOLIA_RPC_URL"),
    "arbitrum": os.getenv("ARBITRUM_RPC_URL"),
}


# ============================================================
# Known on-chain addresses (used only in fork mode)
# ============================================================

FORK_ADDRESSES = {
    "mainnet": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606EB48",
        "WETH": "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2",
        "UNISWAP_V2_ROUTER": "0x7a250d5630B4cF539739df2C5dAcb4c659F2488D",
        "AAVE_ORACLE": "0x54586bE62E3c3580375aE3723C145253060Ca0C2",
    }
}


# ============================================================
# Fork bootstrap
# ============================================================

def fork_is_active() -> bool:
    return FORK_ENABLED


def get_rpc_url() -> str:
    if not fork_is_active():
        raise RuntimeError("Fork not enabled")
    return RPC_URLS[FORK_NETWORK]


def get_fork_block() -> int:
    return FORK_BLOCK


def get_address(name: str) -> str:
    """
    Retourne une adresse réelle uniquement en mode fork
    """
    if not fork_is_active():
        raise RuntimeError("Fork addresses accessed without fork enabled")

    try:
        return FORK_ADDRESSES[FORK_NETWORK][name]
    except KeyError:
        raise KeyError(f"Unknown fork address: {name}")


# ============================================================
# Brownie helpers
# ============================================================

def brownie_fork_setup(network):
    """
    Active le fork Brownie si nécessaire
    """
    if not fork_is_active():
        return

    rpc = get_rpc_url()
    block = get_fork_block()

    network.disconnect()
    network.connect("development")

    network.web3.provider.make_request(
        "hardhat_reset",
        [{
            "forking": {
                "jsonRpcUrl": rpc,
                "blockNumber": block,
            }
        }]
    )


def brownie_impersonate(account_address):
    """
    Impersonation safe (fork only)
    """
    if not fork_is_active():
        raise RuntimeError("Impersonation requires fork mode")

    from brownie import accounts, network

    network.web3.provider.make_request(
        "hardhat_impersonateAccount",
        [account_address]
    )

    return accounts.at(account_address, force=True)


# ============================================================
# Funding helpers
# ============================================================

def fund_account(token, from_whale, to, amount):
    """
    Utilisé pour :
    - transférer USDC / WETH depuis une whale
    - bootstrapper les tests fork
    """
    token.transfer(
        to,
        amount,
        {"from": from_whale}
    )