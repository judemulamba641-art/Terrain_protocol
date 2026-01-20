"""
Risk Engine
-----------
Evaluates health & liquidation risk of NFT-backed loans
"""

from typing import Dict
from ltv_calculator import compute_ltv

# -------------------------------------------------
# THRESHOLDS
# -------------------------------------------------

SAFE_HF = 1.5
WARNING_HF = 1.1
LIQUIDATION_HF = 1.0

# -------------------------------------------------
# CORE LOGIC
# -------------------------------------------------

def assess_position(
    token_id: int,
    price: int,
    debt: int,
    rarity: str = "COMMON",
    volatility: float = 0.0,
    zone_risk: float = 0.0
) -> Dict:
    """
    Assess NFT lending position risk
    """

    ltv_data = compute_ltv(
        price=price,
        rarity=rarity,
        volatility=volatility,
        zone_risk=zone_risk
    )

    hf = float("inf")
    if debt > 0:
        hf = price / debt

    if hf >= SAFE_HF:
        status = "SAFE"
        action = "NONE"
    elif hf >= WARNING_HF:
        status = "WARNING"
        action = "NOTIFY"
    elif hf >= LIQUIDATION_HF:
        status = "DANGER"
        action = "PREPARE_LIQUIDATION"
    else:
        status = "LIQUIDATABLE"
        action = "LIQUIDATE"

    risk_score = min(
        100,
        int((1 / max(hf, 0.01)) * 50)
    )

    return {
        "token_id": token_id,
        "price": price,
        "debt": debt,
        "health_factor": round(hf, 3),
        "risk_score": risk_score,
        "status": status,
        "recommended_action": action,
        "ltv": ltv_data["ltv"],
        "borrow_limit": ltv_data["borrow_limit"],
        "liquidation_threshold": ltv_data["liquidation_threshold"],
    }