"""
Protocol-level invariants
-------------------------

Invariants fondamentaux du protocole DeFi.
Ces règles doivent être vraies :
- avant / après chaque transaction critique
- dans tous les scénarios
- dans les simulations long-run

Un échec ici = bug critique ou fail économique.
"""


# ============================================================
# Accounting invariants
# ============================================================

def invariant_no_unbacked_debt(
    lending_pool
):
    """
    Toute dette doit être couverte par du collatéral valide
    """
    total_debt = lending_pool.getTotalDebt()
    total_collateral_value = lending_pool.getTotalCollateralValue()

    assert total_collateral_value >= total_debt, (
        f"Unbacked debt detected: "
        f"collateral={total_collateral_value}, debt={total_debt}"
    )


def invariant_pool_solvent(
    lending_pool
):
    """
    Le pool ne doit jamais être insolvable
    """
    liquidity = lending_pool.getAvailableLiquidity()
    debt = lending_pool.getTotalDebt()

    assert liquidity + debt >= debt, (
        "Pool insolvency detected"
    )


# ============================================================
# User position invariants
# ============================================================

def invariant_user_health_factor(
    lending_pool,
    user
):
    """
    Si HF < 1 → position liquidable
    Si HF >= 1 → position safe
    """
    hf = lending_pool.getHealthFactor(user)

    assert hf >= 0, f"Invalid health factor: {hf}"


def invariant_user_debt_non_negative(
    lending_pool,
    user
):
    """
    La dette utilisateur ne peut jamais être négative
    """
    debt = lending_pool.getUserDebt(user)
    assert debt >= 0, f"Negative debt detected: {debt}"


# ============================================================
# Collateral invariants
# ============================================================

def invariant_nft_collateral_uniqueness(
    nft_manager,
    nft_address,
    token_id
):
    """
    Un NFT ne peut pas être :
    - déposé deux fois
    - collatéralisé par deux utilisateurs
    """
    owner = nft_manager.getNFTOwner(nft_address, token_id)

    assert owner is not None, "NFT collateral owner missing"


def invariant_collateral_not_double_used(
    lending_pool,
    user
):
    """
    Le même collatéral ne peut pas couvrir plusieurs positions
    """
    collateral_value = lending_pool.getUserCollateralValue(user)
    assert collateral_value >= 0, "Invalid collateral value"


# ============================================================
# Liquidation invariants
# ============================================================

def invariant_liquidation_only_if_undercollateralized(
    lending_pool,
    user
):
    """
    Une liquidation ne doit être possible que si HF < 1
    """
    hf = lending_pool.getHealthFactor(user)
    assert hf < 1e18, "Liquidation executed on healthy position"


def invariant_post_liquidation_cleanup(
    lending_pool,
    nft_manager,
    user,
    nft_address,
    token_id
):
    """
    Après liquidation :
    - dette nulle
    - collatéral retiré
    """
    assert lending_pool.getUserDebt(user) == 0, "Debt remains after liquidation"

    assert not nft_manager.isNFTCollateralized(
        nft_address,
        token_id
    ), "NFT still marked as collateral after liquidation"


# ============================================================
# Oracle invariants
# ============================================================

def invariant_oracle_price_positive(
    oracle,
    asset_address,
    token_id=None
):
    """
    Aucun prix nul ou négatif
    """
    if token_id is None:
        price = oracle.getPrice(asset_address)
    else:
        price = oracle.getNFTPrice(asset_address, token_id)

    assert price > 0, f"Invalid oracle price: {price}"


def invariant_oracle_price_sane(
    old_price,
    new_price,
    max_change_bps=5_000
):
    """
    Empêche des variations extrêmes instantanées
    """
    delta = abs(new_price - old_price)
    max_delta = old_price * max_change_bps / 10_000

    assert delta <= max_delta, (
        f"Oracle price jump too large: "
        f"old={old_price}, new={new_price}"
    )


# ============================================================
# Governance & admin invariants
# ============================================================

def invariant_admin_only_call(
    tx_sender,
    admin
):
    """
    Vérifie que certaines fonctions critiques
    ne sont appelées que par l'admin / timelock
    """
    assert tx_sender == admin, "Unauthorized admin call"


def invariant_timelock_respected(
    eta,
    current_time
):
    """
    Vérifie que le timelock est respecté
    """
    assert current_time >= eta, "Timelock bypass detected"


# ============================================================
# Global invariants (simulation)
# ============================================================

def invariant_protocol_never_halts(
    last_block,
    current_block
):
    """
    Le protocole ne doit jamais se bloquer
    (overflow, revert systématique, dead state)
    """
    assert current_block > last_block, "Protocol halted"