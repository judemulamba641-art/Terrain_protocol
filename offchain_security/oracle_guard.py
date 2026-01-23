from web3 import Web3
from statistics import median
from config import NFT_PRICE_MAX_DEVIATION

def check_nft_price(prices: list[float]) -> bool:
    med = median(prices)
    for p in prices:
        if abs(p - med) / med > NFT_PRICE_MAX_DEVIATION:
            return False
    return True
