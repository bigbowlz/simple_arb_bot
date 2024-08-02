'''
balances.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 0.0.1
'''
from decimal import Decimal
from web3 import Web3

def to_wei(amount, decimals):
    return int(Decimal(amount) * 10**decimals)

def from_wei(amount_in_wei, decimals):
    return int(Decimal(amount_in_wei) / (10**decimals))

def sign_and_send_tx(web3, tx, private_key):
  signed_tx = web3.eth.account.sign_transaction(tx, private_key)
  tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  return tx_receipt

'''from populate_routes import (setup)

def get_ERC20_balance(accountAddress, assetAddress):
    
    Gets and logs the balance of an asset in an account. 
    
    return {} #{assetAddress: balance}

def get_ETH_balance(accountAddress, assetAddress):
'''

