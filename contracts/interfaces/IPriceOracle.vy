# @version ^0.3.10

"""
IPriceOracle Interface
Used by LendingPool, LiquidationManager, Governance
All prices are returned in 18 decimals
"""

interface IPriceOracle:

    # -------- ERC20 pricing --------

    def getAssetPrice(asset: address) -> uint256: view
    # returns price of ERC20 token (ex: stable, native token)


    # -------- NFT pricing --------

    def getNFTPrice(nft: address, tokenId: uint256) -> uint256: view
    # returns price of a specific NFT (terrain 3D)


    def getNFTFloorPrice(nft: address) -> uint256: view
    # returns collection floor price


    # -------- Helpers --------

    def isPriceValid(asset: address) -> bool: view
    # checks if price is fresh / valid


    def lastUpdate(asset: address) -> uint256: view
    # timestamp of last price update