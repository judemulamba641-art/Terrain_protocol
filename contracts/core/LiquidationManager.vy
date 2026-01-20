# @version ^0.3.10
"""
LiquidationManager.vy
=====================
Handles liquidations with governance control and rate limiting.
"""

# ------------------------------------------------------------
# INTERFACES
# ------------------------------------------------------------

interface LendingPool:
    def seize_nft_collateral(
        borrower: address,
        liquidator: address,
        nft: address,
        nft_id: uint256
    ): nonpayable

interface NFTCollateralManager:
    def health_factor(nft: address, debt: uint256) -> uint256: view

interface LendingPoolView:
    def debts(user: address) -> uint256: view


# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------

governance: public(address)
lending_pool: public(address)
nft_manager: public(address)

paused: public(bool)

max_liquidations_per_block: public(uint256)
liquidations_this_block: uint256
last_block: uint256


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

event LiquidationTriggered:
    borrower: address
    liquidator: address

event Paused:
    status: bool


# ------------------------------------------------------------
# CONSTRUCTOR
# ------------------------------------------------------------

@external
def __init__(
    _governance: address,
    _lending_pool: address,
    _nft_manager: address,
    _max_liquidations_per_block: uint256
):
    assert _governance != empty(address)
    assert _lending_pool != empty(address)
    assert _nft_manager != empty(address)

    self.governance = _governance
    self.lending_pool = _lending_pool
    self.nft_manager = _nft_manager
    self.max_liquidations_per_block = _max_liquidations_per_block

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


@internal
def _rate_limit():
    if block.number != self.last_block:
        self.liquidations_this_block = 0
        self.last_block = block.number

    assert self.liquidations_this_block < self.max_liquidations_per_block
    self.liquidations_this_block += 1


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
def set_max_liquidations_per_block(value: uint256):
    self._only_governance()
    assert value > 0
    self.max_liquidations_per_block = value


# ------------------------------------------------------------
# LIQUIDATION
# ------------------------------------------------------------

@external
def liquidate(
    borrower: address,
    nft: address,
    nft_id: uint256
):
    self._not_paused()
    self._rate_limit()

    debt: uint256 = LendingPoolView(self.lending_pool).debts(borrower)
    assert debt > 0

    hf: uint256 = NFTCollateralManager(self.nft_manager).health_factor(
        nft,
        debt
    )

    # HF < 1 => liquidatable
    assert hf < 10**18

    LendingPool(self.lending_pool).seize_nft_collateral(
        borrower,
        msg.sender,
        nft,
        nft_id
    )

    log LiquidationTriggered(borrower, msg.sender)