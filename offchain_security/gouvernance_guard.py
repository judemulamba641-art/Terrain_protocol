import time
from config import MAX_MINT_PER_DAY

minted_today = 0
last_reset = time.time()

def can_mint(amount):
    global minted_today, last_reset
    if time.time() - last_reset > 86400:
        minted_today = 0
        last_reset = time.time()

    return minted_today + amount <= MAX_MINT_PER_DAY

def register_mint(amount):
    global minted_today
    minted_today += amount
