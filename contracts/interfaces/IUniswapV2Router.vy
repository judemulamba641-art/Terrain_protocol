# @version ^0.3.10

"""
IUniswapV2Router Interface
Compatible with Uniswap V2 & forks
"""

interface IUniswapV2Router:

    # -------- Liquidity --------

    def addLiquidity(
        tokenA: address,
        tokenB: address,
        amountADesired: uint256,
        amountBDesired: uint256,
        amountAMin: uint256,
        amountBMin: uint256,
        to: address,
        deadline: uint256
    ) -> (uint256, uint256, uint256): nonpayable

    def removeLiquidity(
        tokenA: address,
        tokenB: address,
        liquidity: uint256,
        amountAMin: uint256,
        amountBMin: uint256,
        to: address,
        deadline: uint256
    ) -> (uint256, uint256): nonpayable


    # -------- Swaps --------

    def swapExactTokensForTokens(
        amountIn: uint256,
        amountOutMin: uint256,
        path: address[3],
        to: address,
        deadline: uint256
    ) -> uint256[3]: nonpayable


    def swapTokensForExactTokens(
        amountOut: uint256,
        amountInMax: uint256,
        path: address[3],
        to: address,
        deadline: uint256
    ) -> uint256[3]: nonpayable


    # -------- Helpers --------

    def getAmountsOut(
        amountIn: uint256,
        path: address[3]
    ) -> uint256[3]: view

    def getAmountsIn(
        amountOut: uint256,
        path: address[3]
    ) -> uint256[3]: view