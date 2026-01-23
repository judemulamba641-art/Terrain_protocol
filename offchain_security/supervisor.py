from oracle_guard import check_nft_price
from governance_guard import can_mint
from keeper_guard import has_active_keepers
from circuit_breaker import trigger
from alerting import send_alert

def supervise(state):
    if not check_nft_price(state["nft_prices"]):
        trigger("NFT oracle deviation")
        send_alert("NFT price manipulation detected")

    if not has_active_keepers():
        trigger("Keeper failure")
        send_alert("Insufficient keepers")

    if not can_mint(state["mint_amount"]):
        trigger("Excessive mint")
        send_alert("Mint cap exceeded")
