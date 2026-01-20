# @version ^0.3.10

"""
Math Utilities Library
Safe math helpers for DeFi protocols
All operations assume uint256
"""

# -------------------------
# Constants
# -------------------------

WAD: constant(uint256) = 10**18
RAY: constant(uint256) = 10**27
HALF_WAD: constant(uint256) = 5 * 10**17
HALF_RAY: constant(uint256) = 5 * 10**26


# -------------------------
# Basic math
# -------------------------

@internal
@pure
def min(a: uint256, b: uint256) -> uint256:
    return a if a < b else b


@internal
@pure
def max(a: uint256, b: uint256) -> uint256:
    return a if a > b else b


# -------------------------
# WAD math (18 decimals)
# -------------------------

@internal
@pure
def wad_mul(a: uint256, b: uint256) -> uint256:
    if a == 0 or b == 0:
        return 0
    return (a * b + HALF_WAD) / WAD


@internal
@pure
def wad_div(a: uint256, b: uint256) -> uint256:
    assert b != 0, "DIV_BY_ZERO"
    return (a * WAD + b / 2) / b


# -------------------------
# RAY math (27 decimals)
# -------------------------

@internal
@pure
def ray_mul(a: uint256, b: uint256) -> uint256:
    if a == 0 or b == 0:
        return 0
    return (a * b + HALF_RAY) / RAY


@internal
@pure
def ray_div(a: uint256, b: uint256) -> uint256:
    assert b != 0, "DIV_BY_ZERO"
    return (a * RAY + b / 2) / b


# -------------------------
# Percentage math
# basis points (10000 = 100%)
# -------------------------

@internal
@pure
def percent_mul(value: uint256, bp: uint256) -> uint256:
    return (value * bp) / 10_000


@internal
@pure
def percent_div(value: uint256, bp: uint256) -> uint256:
    assert bp != 0, "DIV_BY_ZERO"
    return (value * 10_000) / bp


# -------------------------
# Interest helpers
# -------------------------

@internal
@pure
def linear_interest(rate: uint256, time_delta: uint256) -> uint256:
    # rate in RAY, time in seconds
    return RAY + (rate * time_delta) / 365 days


@internal
@pure
def compounded_interest(rate: uint256, time_delta: uint256) -> uint256:
    # Approximation: (1 + r * t)
    return RAY + (rate * time_delta) / 365 days


# -------------------------
# Health factor
# -------------------------

@internal
@pure
def health_factor(
    collateral_value: uint256,
    debt_value: uint256,
    liquidation_threshold_bp: uint256
) -> uint256:
    if debt_value == 0:
        return type(uint256).max

    adjusted_collateral: uint256 = percent_mul(
        collateral_value,
        liquidation_threshold_bp
    )

    return wad_div(adjusted_collateral, debt_value)