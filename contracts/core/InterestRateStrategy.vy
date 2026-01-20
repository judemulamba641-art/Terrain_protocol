# @version ^0.3.10

"""
Interest Rate Strategy (Aave-like)
Calculates borrow interest rate based on utilization
"""

# -------------------------
# Storage
# -------------------------

owner: public(address)

# Rates are in RAY (1e27)
RAY: constant(uint256) = 10**27

base_rate: public(uint256)          # base borrow rate
slope1: public(uint256)             # rate below optimal
slope2: public(uint256)             # rate above optimal
optimal_utilization: public(uint256)  # 0–10000 (e.g 8000 = 80%)


# -------------------------
# Constructor
# -------------------------

@external
def __init__():
    self.owner = msg.sender

    # Default Aave-like values
    self.base_rate = 2 * 10**25       # 2%
    self.slope1 = 4 * 10**25          # +4%
    self.slope2 = 75 * 10**25         # +75%
    self.optimal_utilization = 8000   # 80%


# -------------------------
# DAO setters
# -------------------------

@external
def setParameters(
    _base: uint256,
    _slope1: uint256,
    _slope2: uint256,
    _optimal: uint256
):
    assert msg.sender == self.owner, "DAO only"
    assert _optimal <= 10000, "Invalid optimal"

    self.base_rate = _base
    self.slope1 = _slope1
    self.slope2 = _slope2
    self.optimal_utilization = _optimal


# -------------------------
# Interest calculation
# -------------------------

@external
@view
def getBorrowRate(
    totalBorrowed: uint256,
    totalLiquidity: uint256
) -> uint256:
    """
    Returns borrow rate per year (RAY)
    """

    if totalBorrowed == 0 or totalLiquidity == 0:
        return self.base_rate

    utilization: uint256 = totalBorrowed * 10000 / totalLiquidity

    if utilization <= self.optimal_utilization:
        # Linear increase below optimal
        return self.base_rate + (
            utilization * self.slope1 / self.optimal_utilization
        )

    # Above optimal utilization
    excess: uint256 = utilization - self.optimal_utilization
    excess_ratio: uint256 = excess * 10000 / (10000 - self.optimal_utilization)

    return (
        self.base_rate
        + self.slope1
        + (excess_ratio * self.slope2 / 10000)
    )