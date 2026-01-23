keepers = set()

def register_keeper(addr):
    keepers.add(addr)

def has_active_keepers():
    return len(keepers) >= 3
