# @version ^0.3.10

"""
Native Token for DeFi Terrain Protocol
ERC20 compatible
"""

# -------------------------
# Events
# -------------------------

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event OwnershipTransferred:
    old_owner: address
    new_owner: address


# -------------------------
# Storage
# -------------------------

name: public(String[64])
symbol: public(String[16])
decimals: public(uint256)

total_supply: public(uint256)
max_supply: public(uint256)

balances: HashMap[address, uint256]
allowances: HashMap[address, HashMap[address, uint256]]

owner: public(address)


# -------------------------
# Constructor
# -------------------------

@external
def __init__(
    _name: String[64],
    _symbol: String[16],
    _max_supply: uint256
):
    self.name = _name
    self.symbol = _symbol
    self.decimals = 18

    self.owner = msg.sender
    self.max_supply = _max_supply


# -------------------------
# ERC20 logic
# -------------------------

@external
def balanceOf(account: address) -> uint256:
    return self.balances[account]


@external
def allowance(owner_: address, spender: address) -> uint256:
    return self.allowances[owner_][spender]


@external
def transfer(to: address, amount: uint256) -> bool:
    assert amount > 0, "Amount zero"
    assert self.balances[msg.sender] >= amount, "Insufficient balance"

    self.balances[msg.sender] -= amount
    self.balances[to] += amount

    log Transfer(msg.sender, to, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowances[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True


@external
def transferFrom(
    from_: address,
    to: address,
    amount: uint256
) -> bool:
    assert amount > 0, "Amount zero"
    assert self.balances[from_] >= amount, "Balance too low"
    assert self.allowances[from_][msg.sender] >= amount, "Allowance too low"

    self.allowances[from_][msg.sender] -= amount
    self.balances[from_] -= amount
    self.balances[to] += amount

    log Transfer(from_, to, amount)
    return True


# -------------------------
# Mint / Burn
# -------------------------

@external
def mint(to: address, amount: uint256):
    assert msg.sender == self.owner, "Not authorized"
    assert self.total_supply + amount <= self.max_supply, "Max supply exceeded"

    self.total_supply += amount
    self.balances[to] += amount

    log Transfer(ZERO_ADDRESS, to, amount)


@external
def burn(amount: uint256):
    assert self.balances[msg.sender] >= amount, "Insufficient balance"

    self.balances[msg.sender] -= amount
    self.total_supply -= amount

    log Transfer(msg.sender, ZERO_ADDRESS, amount)


# -------------------------
# Ownership
# -------------------------

@external
def transferOwnership(new_owner: address):
    assert msg.sender == self.owner, "Not authorized"
    assert new_owner != ZERO_ADDRESS, "Invalid address"

    old_owner: address = self.owner
    self.owner = new_owner

    log OwnershipTransferred(old_owner, new_owner)