# @version ^0.3.10

"""
Terrain NFT
Represents a 3D virtual land usable as DeFi collateral
ERC721 compatible
"""

# -------------------------
# Events
# -------------------------

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    tokenId: indexed(uint256)

event Approval:
    owner: indexed(address)
    approved: indexed(address)
    tokenId: indexed(uint256)

event ApprovalForAll:
    owner: indexed(address)
    operator: indexed(address)
    approved: bool


# -------------------------
# Storage
# -------------------------

name: public(String[64])
symbol: public(String[16])

owner: public(address)

total_supply: public(uint256)

owners: HashMap[uint256, address]
balances: HashMap[address, uint256]

token_approvals: HashMap[uint256, address]
operator_approvals: HashMap[address, HashMap[address, bool]]

# Terrain metadata
token_uri: HashMap[uint256, String[256]]
zone: HashMap[uint256, String[64]]
surface: HashMap[uint256, uint256]
rarity: HashMap[uint256, uint256]

# DeFi lock (collateral)
locked: public(HashMap[uint256, bool])


# -------------------------
# Constructor
# -------------------------

@external
def __init__(_name: String[64], _symbol: String[16]):
    self.name = _name
    self.symbol = _symbol
    self.owner = msg.sender


# -------------------------
# ERC721 core
# -------------------------

@external
def balanceOf(account: address) -> uint256:
    assert account != ZERO_ADDRESS, "Zero address"
    return self.balances[account]


@external
def ownerOf(tokenId: uint256) -> address:
    owner: address = self.owners[tokenId]
    assert owner != ZERO_ADDRESS, "Token does not exist"
    return owner


@external
def approve(to: address, tokenId: uint256):
    owner: address = self.ownerOf(tokenId)
    assert msg.sender == owner or self.operator_approvals[owner][msg.sender], "Not authorized"
    assert not self.locked[tokenId], "NFT locked"

    self.token_approvals[tokenId] = to
    log Approval(owner, to, tokenId)


@external
def getApproved(tokenId: uint256) -> address:
    return self.token_approvals[tokenId]


@external
def setApprovalForAll(operator: address, approved: bool):
    self.operator_approvals[msg.sender][operator] = approved
    log ApprovalForAll(msg.sender, operator, approved)


@external
def isApprovedForAll(owner: address, operator: address) -> bool:
    return self.operator_approvals[owner][operator]


@external
def transferFrom(from_: address, to: address, tokenId: uint256):
    assert not self.locked[tokenId], "NFT locked"
    assert self.ownerOf(tokenId) == from_, "Not owner"
    assert (
        msg.sender == from_
        or msg.sender == self.token_approvals[tokenId]
        or self.operator_approvals[from_][msg.sender]
    ), "Not authorized"

    self._transfer(from_, to, tokenId)


@internal
def _transfer(from_: address, to: address, tokenId: uint256):
    self.token_approvals[tokenId] = ZERO_ADDRESS

    self.balances[from_] -= 1
    self.balances[to] += 1
    self.owners[tokenId] = to

    log Transfer(from_, to, tokenId)


# -------------------------
# Mint (DAO / Admin)
# -------------------------

@external
def mint(
    to: address,
    _uri: String[256],
    _zone: String[64],
    _surface: uint256,
    _rarity: uint256
):
    assert msg.sender == self.owner, "Not authorized"
    assert to != ZERO_ADDRESS, "Zero address"

    tokenId: uint256 = self.total_supply + 1

    self.total_supply = tokenId
    self.owners[tokenId] = to
    self.balances[to] += 1

    self.token_uri[tokenId] = _uri
    self.zone[tokenId] = _zone
    self.surface[tokenId] = _surface
    self.rarity[tokenId] = _rarity

    log Transfer(ZERO_ADDRESS, to, tokenId)


# -------------------------
# Metadata
# -------------------------

@external
def tokenURI(tokenId: uint256) -> String[256]:
    assert self.owners[tokenId] != ZERO_ADDRESS, "Token does not exist"
    return self.token_uri[tokenId]


# -------------------------
# DeFi collateral lock
# -------------------------

@external
def lock(tokenId: uint256):
    assert msg.sender == self.owner, "Only protocol"
    self.locked[tokenId] = True


@external
def unlock(tokenId: uint256):
    assert msg.sender == self.owner, "Only protocol"
    self.locked[tokenId] = False


# -------------------------
# Ownership
# -------------------------

@external
def transferOwnership(new_owner: address):
    assert msg.sender == self.owner, "Not authorized"
    assert new_owner != ZERO_ADDRESS, "Invalid address"
    self.owner = new_owner