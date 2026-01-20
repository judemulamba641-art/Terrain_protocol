import pytest


def test_pause_blocks_borrow(protocol, borrower, guardian):
    pool = protocol["lending_pool"]

    pool.pause(sender=guardian)

    with pytest.raises(Exception):
        pool.borrow(
            1000,
            protocol["nft"].address,
            1,
            sender=borrower
        )