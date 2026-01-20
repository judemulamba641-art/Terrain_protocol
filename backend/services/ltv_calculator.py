"""
LTV Calculator
--------------
Computes Loan-To-Value ratios for terrain NFTs
"""

from typing import Dict

# -------------------------------------------------
# CONFIG (can be moved to DAO later)
# -------------------------------------------------

BASE_LTV = 0.50                  # 50%
MAX_LTV = 0.65                   # 65%
LIQUIDATION_THRESHOLD = 0.75     # 75%

RARITY_BONUS = {
    "COMMON": 0.00,
    "RARE": 0.05,
    "EPIC": 0.10,
    "LEGENDARY": 0.15,
}

# -------------------------------------------------
# CORE LOGIC
# -------------------------------------------------

def compute_ltv(
    price: int,
    rarity: str = "COMMON",
    volatility: float = 0.0,
    zone_risk: float = 0.0
) -> Dict:
    """
    Compute LTV parameters for an NFT terrain

    price        : NFT value
    rarity       : COMMON | RARE | EPIC | LEGENDARY
    volatility   : 0 → 1
    zone_risk    : 0 → 1
    """

    ltv = BASE_LTV
    ltv += RARITY_BONUS.get(rarity.upper(), 0)

    # Risk adjustments
    ltv -= volatility * 0.20
    ltv -= zone_risk * 0.15

    ltv = min(max(ltv, 0.10), MAX_LTV)

    return {
        "ltv": round(ltv, 4),
        "borrow_limit": int(price * ltv),
        "liquidation_threshold": int(price * LIQUIDATION_THRESHOLD),
    }