# @version ^0.3.10

"""
Terrain NFT Marketplace
Native token payments
"""

# -------------------------
# Interfaces
# -------------------------

interface TerrainNFT:
    def ownerOf(tokenId: uint256) -> address: view
    def transferFrom(from_: address, to: address, tokenId: uint256): nonpayable
    def locked(tokenId: uint256) -> bool: view

interface ERC20:
    def transferFrom(from_: address, to: address, amount: uint256) -> bool: nonpayable


# -------------------------
# Events
# -------------------------

event Listed:
    seller: indexed(address)
    tokenId: indexed(uint256)
    price: uint256

event Sale:
    buyer: indexed(address)
    tokenId: indexed(uint256)
    price: uint256

event Cancel:
    seller: indexed(address)
    tokenId: indexed(uint256)


# -------------------------
# Storage
# -------------------------

owner: public(address)

terrain_nft: public(address)
payment_token: public(address)

# tokenId => price
listings: public(HashMap[uint256, uint256])

# tokenId => seller
sellers: public(HashMap[uint256, address])


# -------------------------
# Constructor
# -------------------------

@external
def __init__(_nft: address, _token: address):
    self.owner = msg.sender
    self.terrain_nft = _nft
    self.payment_token = _token


# -------------------------
# List NFT
# -------------------------

@external
def list(tokenId: uint256, price: uint256):
    assert price > 0, "Invalid price"

    nft: TerrainNFT = TerrainNFT(self.terrain_nft)

    assert nft.ownerOf(tokenId) == msg.sender, "Not owner"
    assert not nft.locked(tokenId), "NFT locked"

    self.listings[tokenId] = price
    self.sellers[tokenId] = msg.sender

    log Listed(msg.sender, tokenId, price)


# -------------------------
# Buy NFT
# -------------------------

@external
def buy(tokenId: uint256):
    price: uint256 = self.listings[tokenId]
    seller: address = self.sellers[tokenId]

    assert price > 0, "Not listed"
    assert seller != ZERO_ADDRESS, "Invalid seller"

    token: ERC20 = ERC20(self.payment_token)

    assert token.transferFrom(msg.sender, seller, price)

    nft: TerrainNFT = TerrainNFT(self.terrain_nft)
    nft.transferFrom(seller, msg.sender, tokenId)

    self.listings[tokenId] = 0
    self.sellers[tokenId] = ZERO_ADDRESS

    log Sale(msg.sender, tokenId, price)


# -------------------------
# Cancel listing
# -------------------------

@external
def cancel(tokenId: uint256):
    assert self.sellers[tokenId] == msg.sender, "Not seller"

    self.listings[tokenId] = 0
    self.sellers[tokenId] = ZERO_ADDRESS

    log Cancel(msg.sender, tokenId)