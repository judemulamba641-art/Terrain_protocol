"""
Déploiement du protocole DeFi (version test)
- LendingPool
- NFTCollateralManager
- LiquidationManager
- Oracle mock
- ERC20 + NFT mocks
"""

def deploy_protocol(
    deployer,
    LendingPool,
    NFTCollateralManager,
    LiquidationManager,
    ERC20Mock,
    NFTMock,
    OracleMock
):
    # ------------------
    # Deploy mocks
    # ------------------
    stablecoin = ERC20Mock.deploy(
        "USD Stable",
        "USDS",
        18,
        {"from": deployer}
    )

    protocol_token = ERC20Mock.deploy(
        "Protocol Token",
        "PROTO",
        18,
        {"from": deployer}
    )

    land_nft = NFTMock.deploy(
        "3D Land",
        "LAND",
        {"from": deployer}
    )

    oracle = OracleMock.deploy({"from": deployer})

    # ------------------
    # Deploy core protocol
    # ------------------
    lending_pool = LendingPool.deploy(
        stablecoin.address,
        oracle.address,
        {"from": deployer}
    )

    nft_manager = NFTCollateralManager.deploy(
        lending_pool.address,
        land_nft.address,
        {"from": deployer}
    )

    liquidation_manager = LiquidationManager.deploy(
        lending_pool.address,
        nft_manager.address,
        {"from": deployer}
    )

    # ------------------
    # Wire contracts
    # ------------------
    lending_pool.setCollateralManager(
        nft_manager.address,
        {"from": deployer}
    )

    lending_pool.setLiquidationManager(
        liquidation_manager.address,
        {"from": deployer}
    )

    # ------------------
    # Initial protocol params (safe defaults)
    # ------------------
    lending_pool.setLiquidationThreshold(
        75_00,  # 75%
        {"from": deployer}
    )

    lending_pool.setLiquidationBonus(
        5_00,  # 5%
        {"from": deployer}
    )

    return {
        "stablecoin": stablecoin,
        "protocol_token": protocol_token,
        "land_nft": land_nft,
        "oracle": oracle,
        "lending_pool": lending_pool,
        "nft_manager": nft_manager,
        "liquidation_manager": liquidation_manager,
    }