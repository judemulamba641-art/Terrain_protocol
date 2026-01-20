# @version ^0.3.10
"""
LendingPool.vy
==============
NFT-backed lending pool with governance, liquidation and interest accrual.
Audit-ready V1 design.
"""

# ------------------------------------------------------------
# INTERFACES
# ------------------------------------------------------------

interface ERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(frm: address, to: address, amount: uint256) -> bool: nonpayable
    def balanceOf(owner: address) -> uint256: view


interface NFTCollateralManager:
    def validate_nft_collateral(
        borrower: address,
        nft: address,
        nft_id: uint256,
        borrow_amount: uint256
    ) -> bool: view

    def seize_nft(
        borrower: address,
        liquidator: address,
        nft: address,
        nft_id: uint256
    ): nonpayable


interface InterestRateModel:
    def get_borrow_rate(utilization_bps: uint256) -> uint256: view


# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------

# governance & modules
governance: public(address)
liquidation_manager: public(address)
nft_manager: public(address)
interest_model: public(address)

# asset
asset: public(address)

# protocol state
paused: public(bool)

# debt accounting
debts: public(HashMap[address, uint256])
total_debt: public(uint256)
last_update: public(HashMap[address, uint256])

# caps
max_total_debt: public(uint256)
max_borrow_per_user: public(uint256)


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

event Borrow:
    user: address
    amount: uint256
    nft: address
    nft_id: uint256

event Repay:
    user: address
    amount: uint256

event Liquidated:
    borrower: address
    liquidator: address
    nft: address
    nft_id: uint256

event Paused:
    status: bool


# ------------------------------------------------------------
# CONSTRUCTOR
# ------------------------------------------------------------

@external
def __init__(
    _asset: address,
    _nft_manager: address,
    _liquidation_manager: address,
    _interest_model: address,
    _governance: address,
    _max_total_debt: uint256,
    _max_borrow_per_user: uint256
):
    assert _asset != empty(address)
    assert _nft_manager != empty(address)
    assert _liquidation_manager != empty(address)
    assert _interest_model != empty(address)
    assert _governance != empty(address)

    self.asset = _asset
    self.nft_manager = _nft_manager
    self.liquidation_manager = _liquidation_manager
    self.interest_model = _interest_model
    self.governance = _governance

    self.max_total_debt = _max_total_debt
    self.max_borrow_per_user = _max_borrow_per_user

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
# INTEREST ACCRUAL
# ------------------------------------------------------------

@internal
def _accrue_interest(user: address):
    last: uint256 = self.last_update[user]
    if last == 0:
        self.last_update[user] = block.timestamp
        return

    elapsed: uint256 = block.timestamp - last
    if elapsed == 0:
        return

    principal: uint256 = self.debts[user]
    if principal == 0:
        self.last_update[user] = block.timestamp
        return

    # simple utilization proxy (V1 safe)
    utilization_bps: uint256 = min(
        self.total_debt * 10_000 / max(ERC20(self.asset).balanceOf(self), 1),
        10_000
    )

    rate_bps: uint256 = InterestRateModel(self.interest_model).get_borrow_rate(
        utilization_bps
    )

    interest: uint256 = principal * rate_bps * elapsed / (10_000 * 365 days)

    self.debts[user] += interest
    self.total_debt += interest
    self.last_update[user] = block.timestamp


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
def set_max_total_debt(amount: uint256):
    self._only_governance()
    self.max_total_debt = amount


@external
def set_max_borrow_per_user(amount: uint256):
    self._only_governance()
    self.max_borrow_per_user = amount


@external
def set_interest_model(new_model: address):
    self._only_governance()
    assert new_model != empty(address)
    self.interest_model = new_model


# ------------------------------------------------------------
# CORE LENDING
# ------------------------------------------------------------

@external
def borrow(
    amount: uint256,
    nft: address,
    nft_id: uint256
):
    self._not_paused()
    assert amount > 0

    self._accrue_interest(msg.sender)

    # caps
    assert self.total_debt + amount <= self.max_total_debt
    assert self.debts[msg.sender] + amount <= self.max_borrow_per_user

    # NFT risk validation
    assert NFTCollateralManager(self.nft_manager).validate_nft_collateral(
        msg.sender,
        nft,
        nft_id,
        amount
    )

    # effects
    self.debts[msg.sender] += amount
    self.total_debt += amount

    # interaction
    assert ERC20(self.asset).transfer(msg.sender, amount)

    log Borrow(msg.sender, amount, nft, nft_id)


@external
def repay(amount: uint256):
    self._not_paused()
    assert amount > 0

    self._accrue_interest(msg.sender)

    debt: uint256 = self.debts[msg.sender]
    assert debt > 0

    repay_amount: uint256 = min(amount, debt)

    # effects
    self.debts[msg.sender] -= repay_amount
    self.total_debt -= repay_amount

    # interaction
    assert ERC20(self.asset).transferFrom(
        msg.sender,
        self,
        repay_amount
    )

    log Repay(msg.sender, repay_amount)


# ------------------------------------------------------------
# LIQUIDATION HOOK
# ------------------------------------------------------------

@external
def seize_nft_collateral(
    borrower: address,
    liquidator: address,
    nft: address,
    nft_id: uint256
):
    assert msg.sender == self.liquidation_manager

    self._accrue_interest(borrower)

    debt: uint256 = self.debts[borrower]
    assert debt > 0

    self.debts[borrower] = 0
    self.total_debt -= debt

    NFTCollateralManager(self.nft_manager).seize_nft(
        borrower,
        liquidator,
        nft,
        nft_id
    )

    log Liquidated(borrower, liquidator, nft, nft_id)