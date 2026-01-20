# @version ^0.3.10

"""
IERC721 Interface
ERC-721 Standard Interface
"""

interface IERC721:

    # -------- Views --------

    def ownerOf(tokenId: uint256) -> address: view
    def balanceOf(owner: address) -> uint256: view
    def getApproved(tokenId: uint256) -> address: view
    def isApprovedForAll(owner: address, operator: address) -> bool: view


    # -------- State changing --------

    def approve(to: address, tokenId: uint256): nonpayable
    def setApprovalForAll(operator: address, approved: bool): nonpayable

    def transferFrom(from_: address, to: address, tokenId: uint256): nonpayable
    def safeTransferFrom(from_: address, to: address, tokenId: uint256): nonpayable


    # -------- Events (documentation) --------
    # event Transfer(from: address, to: address, tokenId: uint256)
    # event Approval(owner: address, approved: address, tokenId: uint256)
    # event ApprovalForAll(owner: address, operator: address, approved: bool)