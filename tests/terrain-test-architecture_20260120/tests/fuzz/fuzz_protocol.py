import random

ACTIONS = ["borrow", "repay", "price_crash", "pause", "unpause"]

def fuzz_protocol(protocol, users, chain, rounds=100):
    pool = protocol["lending_pool"]
    oracle = protocol["oracle"]
    gov = protocol["governance"]

    for _ in range(rounds):
        user = random.choice(users)
        action = random.choice(ACTIONS)

        try:
            if action == "borrow":
                pool.borrow(
                    random.randint(1, 50),
                    protocol["nft"].address,
                    1,
                    sender=user
                )

            elif action == "repay":
                pool.repay(
                    random.randint(1, 50),
                    sender=user
                )

            elif action == "price_crash":
                oracle.set_price(random.randint(10, 100), sender=gov)

            elif action == "pause":
                gov.emergency_execute(
                    pool.address,
                    pool.pause.encode_input(),
                    sender=protocol["guardian"]
                )

            elif action == "unpause":
                gov.queue_action(
                    pool.address,
                    0,
                    pool.unpause.encode_input(),
                    sender=protocol["dao"]
                )

        except Exception:
            pass

        # invariants after every step
        assert pool.total_debt() >= 0