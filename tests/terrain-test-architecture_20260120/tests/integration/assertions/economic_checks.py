"""
Economic checks & invariants
----------------------------

Ce module contient uniquement des assertions économiques.
Aucune logique métier, aucun déploiement.

Utilisation :
- integration tests
- flows
- simulations
- audit & risk validation
"""

from math import isclose


# ============================================================
# Health Factor
# ============================================================

def assert_health_factor_above_one(lending_pool, user):
    """
    Vérifie que l'utilisateur est safe (HF > 1)
    """
    hf = lending_pool.getHealthFactor(user)
    assert hf > 1e18, f"Health factor too low: {hf}"


def assert_health_factor_below_one(lending_pool, user):
    """
    Vérifie que l'utilisateur est liquidable
    """
    hf = lending_pool.getHealthFactor(user)
    assert hf < 1e18, f"Health factor should be < 1, got {hf}"


# ============================================================
# Loan-To-Value (LTV)
# ============================================================

def assert_ltv_respected(
    collateral_value,
    borrowed_amount,
    max_ltv_bps
):
    """
    Vérifie que le borrow respecte le LTV max
    """
    max_borrow = collateral_value * max_ltv_bps / 10_000
    assert borrowed_amount <= max_borrow, (
        f"LTV exceeded: borrowed {borrowed_amount}, "
        f"max allowed {max_borrow}"
    )


# ============================================================
# Liquidation economics
# ============================================================

def assert_liquidation_profitable(
    debt_repaid,
    collateral_value,
    liquidation_bonus_bps
):
    """
    Vérifie que la liquidation est économiquement incitative
    (liquidator ne perd pas d'argent)
    """
    expected_collateral = debt_repaid * (1 + liquidation_bonus_bps / 10_000)

    assert collateral_value >= expected_collateral, (
        "Liquidation not profitable: "
        f"collateral {collateral_value}, "
        f"expected >= {expected_collateral}"
    )


def assert_no_bad_debt(
    lending_pool,
    user
):
    """
    Après liquidation, la dette utilisateur doit être nulle
    """
    debt = lending_pool.getUserDebt(user)
    assert debt == 0, f"Bad debt detected: {debt}"


# ============================================================
# Pool solvency
# ============================================================

def assert_pool_solvency(
    total_liquidity,
    total_debt
):
    """
    Invariant fondamental :
    Le pool doit rester solvable
    """
    assert total_liquidity >= total_debt, (
        f"Pool insolvent: liquidity {total_liquidity}, debt {total_debt}"
    )


# ============================================================
# Precision & rounding
# ============================================================

def assert_close(a, b, tolerance=1e-6):
    """
    Vérifie les erreurs de rounding acceptables
    (utile pour intérêts, indices, etc.)
    """
    assert isclose(a, b, rel_tol=tolerance), (
        f"Values not close: {a} vs {b}"
    )


# ============================================================
# Governance safety (economic)
# ============================================================

def assert_parameter_change_reasonable(
    old_value,
    new_value,
    max_delta_bps=2_000
):
    """
    Empêche des changements économiques brutaux
    (ex: liquidation bonus x5)
    """
    delta = abs(new_value - old_value)
    max_delta = old_value * max_delta_bps / 10_000

    assert delta <= max_delta, (
        f"Parameter change too aggressive: "
        f"old={old_value}, new={new_value}"
    )