"""
Global Settings for DeFi Terrain Protocol
Used by liquidation bots, scripts, monitoring tools
"""

import os
from dotenv import load_dotenv

# -------------------------------------------------
# ENV
# -------------------------------------------------

load_dotenv()

# -------------------------------------------------
# NETWORK
# -------------------------------------------------

RPC_URL = os.getenv("RPC_URL")
CHAIN_ID = int(os.getenv("CHAIN_ID", 1))  # 1 = Ethereum mainnet
NETWORK_NAME = os.getenv("NETWORK_NAME", "mainnet")

# -------------------------------------------------
# BOT WALLET
# -------------------------------------------------

BOT_PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
BOT_ADDRESS = os.getenv("BOT_ADDRESS")

# -------------------------------------------------
# CONTRACT ADDRESSES
# -------------------------------------------------

LENDING_POOL = os.getenv("LENDING_POOL")
LIQUIDATION_MANAGER = os.getenv("LIQUIDATION_MANAGER")
NFT_COLLATERAL_MANAGER = os.getenv("NFT_COLLATERAL_MANAGER")
PRICE_ORACLE = os.getenv("PRICE_ORACLE")

TERRAIN_TOKEN = os.getenv("TERRAIN_TOKEN")
TERRAIN_NFT = os.getenv("TERRAIN_NFT")

TIMELOCK = os.getenv("TIMELOCK")
GOVERNOR = os.getenv("GOVERNOR")

UNISWAP_ROUTER = os.getenv("UNISWAP_ROUTER")

# -------------------------------------------------
# LIQUIDATION PARAMETERS
# -------------------------------------------------

# Health factor < 1 => liquidatable
HEALTH_FACTOR_THRESHOLD = float(
    os.getenv("HEALTH_FACTOR_THRESHOLD", 1.0)
)

# Seconds between scans
CHECK_INTERVAL = int(
    os.getenv("CHECK_INTERVAL", 30)
)

# Max gas limit per liquidation tx
MAX_GAS_LIMIT = int(
    os.getenv("MAX_GAS_LIMIT", 600_000)
)

# -------------------------------------------------
# NFT PARAMETERS
# -------------------------------------------------

NFT_START_ID = int(os.getenv("NFT_START_ID", 0))
NFT_MAX_ID = int(os.getenv("NFT_MAX_ID", 10_000))

# -------------------------------------------------
# SAFETY
# -------------------------------------------------

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
ENABLE_LIQUIDATION = os.getenv("ENABLE_LIQUIDATION", "true").lower() == "true"

# -------------------------------------------------
# VALIDATION
# -------------------------------------------------

def validate():
    required = [
        RPC_URL,
        BOT_PRIVATE_KEY,
        BOT_ADDRESS,
        LENDING_POOL,
        LIQUIDATION_MANAGER,
        NFT_COLLATERAL_MANAGER,
        PRICE_ORACLE,
    ]

    missing = [i for i in required if not i]

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {missing}"
        )

validate()