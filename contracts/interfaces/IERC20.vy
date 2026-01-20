# @version ^0.3.10

"""
IERC20 Interface
ERC-20 Standard Interface
"""

interface IERC20:

    # -------- Views --------

    def name() -> String[64]: view
    def symbol() -> String[32]: view
    def decimals() -> uint256: view

    def totalSupply() -> uint256: view
    def balanceOf(owner: address) -> uint256: view
    def allowance(owner: address, spender: address) -> uint256: view


    # -------- State changing --------

    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def approve(spender: address, amount: uint256) -> bool: nonpayable
    def transferFrom(from_: address, to: address, amount: uint256) -> bool: nonpayable


    # -------- Events (documentation) --------
    # event Transfer(from: address, to: address, value: uint256)
    # event Approval(owner: address, spender: address, value: uint256)