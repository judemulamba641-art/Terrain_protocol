# @version ^0.3.10

interface IERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(frm: address, to: address, amount: uint256) -> bool: nonpayable
    def mint(to: address, amount: uint256): nonpayable

interface ITreasuryDAO:
    def receive_fees(token: address, amount: uint256): nonpayable


asset: public(address)
governance: public(address)
treasury: public(address)

paused: public(bool)

borrow_fee_bps: public(uint256)
lending_fee_bps: public(uint256)

total_liquidity: public(uint256)
total_borrowed: public(uint256)

max_total_borrow: public(uint256)
last_borrow_ts: HashMap[address, uint256]

BORROW_COOLDOWN: constant(uint256) = 300


@external
def __init__(_asset: address, _gov: address, _treasury: address):
    self.asset = _asset
    self.governance = _gov
    self.treasury = _treasury

    self.borrow_fee_bps = 30
    self.lending_fee_bps = 10
    self.max_total_borrow = 10**26
    self.paused = False


# =======================
# INTERNAL RISK LOGIC
# =======================

@internal
def _dynamic_borrow_fee() -> uint256:
    if self.total_liquidity == 0:
        return self.borrow_fee_bps

    util: uint256 = self.total_borrowed * 10_000 / self.total_liquidity

    if util > 9000:
        return 80
    elif util > 7500:
        return 50
    else:
        return self.borrow_fee_bps


# =======================
# CORE LOGIC
# =======================

@external
def deposit(amount: uint256):
    assert not self.paused
    assert IERC20(self.asset).transferFrom(msg.sender, self, amount)
    self.total_liquidity += amount


@external
def borrow(amount: uint256):
    assert not self.paused
    assert block.timestamp >= self.last_borrow_ts[msg.sender] + BORROW_COOLDOWN
    assert self.total_borrowed + amount <= self.max_total_borrow

    fee_bps: uint256 = self._dynamic_borrow_fee()
    fee: uint256 = amount * fee_bps / 10_000
    net: uint256 = amount - fee

    # MINT du token → TREASURY (frais)
    IERC20(self.asset).mint(self.treasury, fee)
    ITreasuryDAO(self.treasury).receive_fees(self.asset, fee)

    # MINT du token → borrower
    IERC20(self.asset).mint(msg.sender, net)

    self.total_borrowed += amount
    self.last_borrow_ts[msg.sender] = block.timestamp


@external
def repay(amount: uint256):
    assert IERC20(self.asset).transferFrom(msg.sender, self, amount)
    self.total_borrowed -= amount


# =======================
# GOVERNANCE
# =======================

@external
def set_fees(borrow_bps: uint256, lending_bps: uint256):
    assert msg.sender == self.governance
    self.borrow_fee_bps = borrow_bps
    self.lending_fee_bps = lending_bps


@external
def set_treasury(t: address):
    assert msg.sender == self.governance
    self.treasury = t


@external
def emergency_pause():
    assert msg.sender == self.governance
    self.paused = True
