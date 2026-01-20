def test_global_debt_cap(protocol, borrower):
    pool = protocol["lending_pool"]

    pool.set_max_total_debt(1000, sender=protocol["governance"])

    with pytest.raises(Exception):
        pool.borrow(
            2000,
            protocol["nft"].address,
            1,
            sender=borrower
        )