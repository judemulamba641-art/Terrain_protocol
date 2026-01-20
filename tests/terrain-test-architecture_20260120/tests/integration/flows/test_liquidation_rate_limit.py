def test_liquidation_rate_limit(protocol, liquidator):
    lm = protocol["liquidation_manager"]

    for _ in range(lm.max_liquidations_per_block()):
        lm.liquidate("0xBorrower", protocol["nft"].address, 1, sender=liquidator)

    with pytest.raises(Exception):
        lm.liquidate("0xBorrower", protocol["nft"].address, 1, sender=liquidator)