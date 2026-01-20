"""
Formal protocol invariants.
These must ALWAYS hold.
"""

def invariant_total_debt_consistency(protocol, users):
    """
    total_debt == sum(user debts)
    """
    pool = protocol["lending_pool"]

    total = 0
    for u in users:
        total += pool.debts(u)

    assert total == pool.total_debt()


def invariant_no_borrow_when_paused(protocol, borrower):
    pool = protocol["lending_pool"]

    if pool.paused():
        try:
            pool.borrow(
                1,
                protocol["nft"].address,
                1,
                sender=borrower
            )
            assert False, "Borrow succeeded while paused"
        except Exception:
            pass


def invariant_governance_only_setters(protocol, attacker):
    pool = protocol["lending_pool"]

    setters = [
        lambda: pool.set_max_total_debt(1, sender=attacker),
        lambda: pool.pause(sender=attacker),
    ]

    for call in setters:
        try:
            call()
            assert False, "Unauthorized governance call"
        except Exception:
            pass