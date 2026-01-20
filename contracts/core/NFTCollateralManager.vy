# @version ^0.3.10
"""
NFTCollateralManager.vy
=======================
Manages NFT collateral risk parameters and validation.
Governance-controlled, audit-ready.
"""

# ------------------------------------------------------------
# INTERFACES
# ------------------------------------------------------------

interface ERC721:
    def ownerOf(tokenId: uint256) -> address: view
    def transferFrom(_from: address, _to: address, _id: uint256): nonpayable


interface PriceOracle:
    def twap_price(nft: address) -> uint256: view


# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------

governance: public(address)
lending_pool: public(address)
oracle: public(address)

# risk parameters
ltv_bps: public(uint256)                    # 6000 = 60%
liquidation_threshold_bps: public(uint256)  # 7500 = 75%
max_debt_per_nft: public(uint256)

paused: public(bool)


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

event RiskParamsUpdated:
    ltv_bps: uint256
    liquidation_threshold_bps: uint256

event Paused:
    status: bool


# ------------------------------------------------------------
# CONSTRUCTOR
# ------------------------------------------------------------

@external
def __init__(
    _governance: address,
    _lending_pool: address,
    _oracle: address,
    _max_debt_per_nft: uint256
):
    assert _governance != empty(address)
    assert _lending_pool != empty(address)
    assert _oracle != empty(address)

    self.governance = _governance
    self.lending_pool = _lending_pool
    self.oracle = _oracle

    self.ltv_bps = 6000
    self.liquidation_threshold_bps = 7500
    self.max_debt_per_nft = _max_debt_per_nft

    self.paused = False


# ------------------------------------------------------------
# INTERNAL GUARDS
# ------------------------------------------------------------

@internal
@view
def _only_governance():
    assert msg.sender == self.governance


@internal
@view
def _not_paused():
    assert not self.paused


# ------------------------------------------------------------
# GOVERNANCE CONTROLS
# ------------------------------------------------------------

@external
def pause():
    self._only_governance()
    self.paused = True
    log Paused(True)


@external
def unpause():
    self._only_governance()
    self.paused = False
    log Paused(False)


@external
def set_risk_params(
    _ltv_bps: uint256,
    _liq_threshold_bps: uint256
):
    self._only_governance()
    assert _ltv_bps > 0
    assert _ltv_bps < _liq_threshold_bps
    assert _liq_threshold_bps <= 9000  # hard safety cap

    self.ltv_bps = _ltv_bps
    self.liquidation_threshold_bps = _liq_threshold_bps

    log RiskParamsUpdated(_ltv_bps, _liq_threshold_bps)


@external
def set_max_debt_per_nft(amount: uint256):
    self._only_governance()
    self.max_debt_per_nft = amount


@external
def set_oracle(new_oracle: address):
    self._only_governance()
    assert new_oracle != empty(address)
    self.oracle = new_oracle


# ------------------------------------------------------------
# CORE LOGIC
# ------------------------------------------------------------

@external
@view
def validate_nft_collateral(
    borrower: address,
    nft: address,
    nft_id: uint256,
    borrow_amount: uint256
) -> bool:
    self._not_paused()
    assert borrow_amount > 0

    # ownership check
    assert ERC721(nft).ownerOf(nft_id) == borrower

    # debt cap per NFT
    assert borrow_amount <= self.max_debt_per_nft

    price: uint256 = PriceOracle(self.oracle).twap_price(nft)
    assert price > 0

    max_borrow: uint256 = price * self.ltv_bps / 10_000
    return borrow_amount <= max_borrow


@external
@view
def health_factor(
    nft: address,
    debt: uint256
) -> uint256:
    """
    HF < 1e18 = liquidatable
    """
    price: uint256 = PriceOracle(self.oracle).twap_price(nft)
    assert price > 0

    collateral_value: uint256 = price * self.liquidation_threshold_bps / 10_000
    return collateral_value * 10**18 / debt if debt > 0 else max_value(uint256)


# ------------------------------------------------------------
# LIQUIDATION HOOK (ONLY LENDING POOL)
# ------------------------------------------------------------

@external
def seize_nft(
    borrower: address,
    liquidator: address,
    nft: address,
    nft_id: uint256
):
    assert msg.sender == self.lending_pool
    ERC721(nft).transferFrom(borrower, liquidator, nft_id)