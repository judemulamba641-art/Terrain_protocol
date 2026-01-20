# @version ^0.3.10

"""
Terrain Price Oracle
DAO controlled oracle for 3D land NFTs
"""

# -------------------------
# Interfaces
# -------------------------

interface TerrainNFT:
    def zone(tokenId: uint256) -> String[64]: view
    def surface(tokenId: uint256) -> uint256: view
    def rarity(tokenId: uint256) -> uint256: view


# -------------------------
# Storage
# -------------------------

owner: public(address)

terrain_nft: public(address)

# Base price per zone (in native token, 18 decimals)
zone_price: public(HashMap[String[64], uint256])

# Rarity multiplier (100 = 1.0x)
rarity_multiplier: public(HashMap[uint256, uint256])

# Global price factor
base_price_per_m2: public(uint256)


# -------------------------
# Events
# -------------------------

event PriceUpdated:
    param: String[32]
    value: uint256


# -------------------------
# Constructor
# -------------------------

@external
def __init__(_terrain_nft: address):
    self.owner = msg.sender
    self.terrain_nft = _terrain_nft

    self.base_price_per_m2 = 10 * 10**18  # default


# -------------------------
# DAO setters
# -------------------------

@external
def setZonePrice(zone: String[64], price: uint256):
    assert msg.sender == self.owner, "DAO only"
    self.zone_price[zone] = price
    log PriceUpdated("ZONE", price)


@external
def setRarityMultiplier(rarity: uint256, multiplier: uint256):
    assert msg.sender == self.owner, "DAO only"
    self.rarity_multiplier[rarity] = multiplier
    log PriceUpdated("RARITY", multiplier)


@external
def setBasePrice(price: uint256):
    assert msg.sender == self.owner, "DAO only"
    self.base_price_per_m2 = price
    log PriceUpdated("BASE", price)


# -------------------------
# Price calculation
# -------------------------

@external
@view
def getTerrainPrice(tokenId: uint256) -> uint256:
    nft: TerrainNFT = TerrainNFT(self.terrain_nft)

    surface: uint256 = nft.surface(tokenId)
    rarity: uint256 = nft.rarity(tokenId)
    zone: String[64] = nft.zone(tokenId)

    base: uint256 = surface * self.base_price_per_m2
    zone_bonus: uint256 = self.zone_price[zone]
    rarity_mult: uint256 = self.rarity_multiplier[rarity]

    if rarity_mult == 0:
        rarity_mult = 100

    return (base + zone_bonus) * rarity_mult / 100