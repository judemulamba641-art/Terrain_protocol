paused = False

def trigger(reason):
    global paused
    paused = True
    print(f"[CIRCUIT BREAKER] PAUSED: {reason}")

def is_paused():
    return paused
