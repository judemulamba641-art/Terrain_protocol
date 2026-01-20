# @version ^0.3.10

"""
Uniswap Liquidity Manager
Adds liquidity for native token
"""

# -------------------------
# Interfaces
# -------------------------

interface ERC20:
    def approve(spender: address, amount: uint256) -> bool: nonpayable
    def transferFrom(sender: address, receiver: address, amount: uint256) -> bool: nonpayable
    def balanceOf(account: address) -> uint256: view

interface UniswapV2Router:
    def addLiquidityETH(
        token: address,
        amountTokenDesired: uint256,
        amountTokenMin: uint256,
        amountETHMin: uint256,
        to: address,
        deadline: uint256
    ) -> (uint256, uint256, uint256): payable


# -------------------------
# Storage
# -------------------------

owner: public(address)

token: public(address)
router: public(address)


# -------------------------
# Constructor
# -------------------------

@external
def __init__(_token: address, _router: address):
    self.owner = msg.sender
    self.token = _token
    self.router = _router


# -------------------------
# Add Liquidity
# -------------------------

@external
@payable
def addLiquidity(amount_token: uint256):
    assert msg.sender == self.owner, "DAO only"
    assert amount_token > 0, "Zero amount"
    assert msg.value > 0, "No ETH sent"

    erc20: ERC20 = ERC20(self.token)
    uni: UniswapV2Router = UniswapV2Router(self.router)

    # Transfer token from DAO
    assert erc20.transferFrom(msg.sender, self, amount_token)

    # Approve router
    assert erc20.approve(self.router, amount_token)

    # Add liquidity
    uni.addLiquidityETH(
        self.token,
        amount_token,
        0,
        0,
        msg.sender,
        block.timestamp + 600
    )