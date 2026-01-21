# contracts/LendingPool.vy
# @version ^0.3.10

interface ERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(frm: address, to: address, amount: uint256) -> bool: nonpayable
    def balanceOf(account: address) -> uint256: view

interface TreasuryDAO:
    def deposit_fees(amount: uint256): nonpayable


asset: public(address)
governance: public(address)
treasury: public(address)

paused: public(bool)

total_liquidity: public(uint256)
total_borrowed: public(uint256)

borrow_fee_bps: public(uint256)
lending_fee_bps: public(uint256)

max_total_borrow: public(uint256)
BORROW_COOLDOWN: constant(uint256) = 300
last_borrow: HashMap[address, uint256]

debts: public(HashMap[address, uint256])


@external
def __init__(_asset: address, _gov: address):
    self.asset = _asset
    self.governance = _gov

    self.borrow_fee_bps = 30
    self.lending_fee_bps = 10
    self.max_total_borrow = 10**26
    self.paused = False


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


@external
def borrow(amount: uint256):
    assert not self.paused, "PAUSED"
    assert block.timestamp >= self.last_borrow[msg.sender] + BORROW_COOLDOWN
    assert self.total_borrowed + amount <= self.max_total_borrow

    fee_bps: uint256 = self._dynamic_borrow_fee()
    fee: uint256 = amount * fee_bps / 10_000
    net: uint256 = amount - fee

    self.total_borrowed += amount
    self.debts[msg.sender] += amount
    self.last_borrow[msg.sender] = block.timestamp

    ERC20(self.asset).transfer(self.treasury, fee)
    TreasuryDAO(self.treasury).deposit_fees(fee)

    ERC20(self.asset).transfer(msg.sender, net)


@external
def repay(amount: uint256):
    assert not self.paused, "PAUSED"
    assert amount <= self.debts[msg.sender]

    fee: uint256 = amount * self.lending_fee_bps / 10_000

    ERC20(self.asset).transferFrom(msg.sender, self.treasury, fee)
    TreasuryDAO(self.treasury).deposit_fees(fee)

    ERC20(self.asset).transferFrom(msg.sender, self, amount)

    self.debts[msg.sender] -= amount
    self.total_borrowed -= amount


@external
def set_fees(borrow_bps: uint256, lending_bps: uint256):
    assert msg.sender == self.governance
    self.borrow_fee_bps = borrow_bps
    self.lending_fee_bps = lending_bps


@external
def set_treasury(_treasury: address):
    assert msg.sender == self.governance
    self.treasury = _treasury


@external
def pause():
    assert msg.sender == self.governance
    self.paused = True
