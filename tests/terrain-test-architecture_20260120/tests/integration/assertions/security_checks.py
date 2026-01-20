"""
Security checks
---------------

Assertions de sécurité visant à détecter :
- accès non autorisés
- états dangereux
- comportements exploitables
- violations de modèles DeFi standards

Un échec ici = vulnérabilité potentielle.
"""

import pytest


# ============================================================
# Access control
# ============================================================

def assert_only_admin(
    tx_sender,
    admin
):
    """
    Vérifie que l'appelant est bien l'admin / timelock
    """
    assert tx_sender == admin, (
        f"Unauthorized access: sender={tx_sender}, admin={admin}"
    )


def assert_not_zero_address(address):
    """
    Empêche l'usage de l'adresse zéro
    """
    assert address != "0x0000000000000000000000000000000000000000", (
        "Zero address used"
    )


# ============================================================
# Reentrancy & state safety
# ============================================================

def assert_no_reentrancy_lock_active(contract):
    """
    Vérifie que le contrat n'est pas bloqué
    par un guard de reentrancy
    """
    if hasattr(contract, "reentrancyLock"):
        assert contract.reentrancyLock() is False, (
            "Reentrancy lock stuck"
        )


def assert_state_updated_before_external_call(
    state_before,
    state_after
):
    """
    Pattern check (checks-effects-interactions)
    """
    assert state_after != state_before, (
        "State not updated before external interaction"
    )


# ============================================================
# Oracle manipulation
# ============================================================

def assert_oracle_price_not_stale(
    last_update,
    current_time,
    max_delay
):
    """
    Empêche l'utilisation de prix obsolètes
    """
    assert current_time - last_update <= max_delay, (
        "Stale oracle price used"
    )


def assert_oracle_cannot_be_set_by_user(
    tx_sender,
    authorized_updater
):
    """
    Seul un keeper / oracle autorisé peut setter les prix
    """
    assert tx_sender == authorized_updater, (
        "Oracle price update by unauthorized user"
    )


# ============================================================
# Borrow & liquidation safety
# ============================================================

def assert_borrow_not_zero(amount):
    """
    Empêche les borrows nuls (edge case griefing)
    """
    assert amount > 0, "Zero borrow amount"


def assert_liquidation_not_self(
    borrower,
    liquidator
):
    """
    Empêche l'auto-liquidation abusive
    """
    assert borrower != liquidator, (
        "Self-liquidation detected"
    )


def assert_liquidation_only_once(
    was_liquidated
):
    """
    Empêche les doubles liquidations
    """
    assert was_liquidated is False, (
        "Double liquidation attempt"
    )


# ============================================================
# NFT-specific security
# ============================================================

def assert_nft_ownership_before_deposit(
    nft_contract,
    token_id,
    user
):
    """
    L'utilisateur doit posséder le NFT avant dépôt
    """
    owner = nft_contract.ownerOf(token_id)
    assert owner == user, (
        f"NFT ownership mismatch: owner={owner}, user={user}"
    )


def assert_nft_not_used_elsewhere(
    nft_manager,
    nft_address,
    token_id
):
    """
    Empêche l'usage du même NFT comme collatéral
    dans plusieurs protocoles / positions
    """
    assert not nft_manager.isNFTCollateralized(
        nft_address,
        token_id
    ), "NFT already used as collateral"


# ============================================================
# Precision & overflow
# ============================================================

def assert_no_overflow(value, max_value=2**256 - 1):
    """
    Détection overflow / underflow
    """
    assert 0 <= value <= max_value, (
        f"Overflow / underflow detected: {value}"
    )


# ============================================================
# Denial-of-service & griefing
# ============================================================

def assert_operation_gas_reasonable(
    gas_used,
    max_gas
):
    """
    Empêche des opérations volontairement coûteuses
    (gas griefing)
    """
    assert gas_used <= max_gas, (
        f"Gas griefing detected: gas={gas_used}"
    )


def assert_no_permanent_lock(
    is_locked
):
    """
    Empêche les états irréversibles
    """
    assert is_locked is False, (
        "Permanent lock detected"
    )


# ============================================================
# Upgrade & governance safety
# ============================================================

def assert_implementation_not_zero(address):
    """
    Proxy safety
    """
    assert_not_zero_address(address)


def assert_upgrade_not_immediate(
    eta,
    current_time
):
    """
    Empêche les upgrades instantanés
    """
    assert current_time < eta, (
        "Immediate upgrade detected"
    )