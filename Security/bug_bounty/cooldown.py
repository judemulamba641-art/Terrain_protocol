import time

last_claim = {}

def can_claim(address):
    now = int(time.time())
    last = last_claim.get(address, 0)
    return now > last + 86400

def register_claim(address):
    last_claim[address] = int(time.time())
