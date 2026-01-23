from web3 import Web3
from config import RPC_URL, PRIVATE_KEY

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

def send_tx(tx):
    tx["nonce"] = w3.eth.get_transaction_count(account.address)
    tx["gasPrice"] = w3.eth.gas_price
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
