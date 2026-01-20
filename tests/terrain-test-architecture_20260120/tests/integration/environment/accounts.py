"""
Centralisation des comptes utilisés dans les tests d'intégration
Permet de garder des scénarios lisibles et auditables
"""

from dataclasses import dataclass

@dataclass
class ProtocolAccounts:
    admin: object
    borrower: object
    lender: object
    liquidator: object
    keeper: object
    treasury: object


def load_accounts(accounts):
    """
    Map explicite des rôles → comptes EVM
    Compatible Brownie / Ape
    """
    return ProtocolAccounts(
        admin=accounts[0],
        borrower=accounts[1],
        lender=accounts[2],
        liquidator=accounts[3],
        keeper=accounts[4],
        treasury=accounts[5],
    )