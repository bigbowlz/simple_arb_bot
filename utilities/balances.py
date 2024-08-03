'''
balances.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 08-04-2024
'''
from decimal import Decimal
from web3 import Web3

def to_wei(amount, decimals):
    """
    Converts amount in eth units to in wei units.

    Params:
        amount (int): Amount in eth.
        decimals (int): The decimals for the conversion. 

    Returns:
        int: amount * 10 ** decimals
    """
    return int(Decimal(amount) * 10**decimals)

def from_wei(amount_in_wei, decimals):
    """
    Converts amount in wei units to in eth units.

    Params:
        amount_in_wei (int): Amount in wei.
        decimals (int): The decimals for the conversion. 

    Returns:
        int: amount / 10 ** decimals
    """
    return int(Decimal(amount_in_wei) / (10**decimals))

def sign_and_send_tx(web3, tx, private_key):
    """
    Sign and send a transaction.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        tx (dict): A dictionary conforming to the web3.eth.send_transaction(transaction) method.
        private_key (str): Hex value of a private key.

    Returns:
        tx_receipt (receipt): the receipt of a transaction.
    """
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt

def get_token_decimals(token_address, web3):
    '''
    Get the number of decimals for a token.

    Params:
        token_address: the string address of the token contract.
        web3: an instance of the Web3 class from the web3.py library.
    '''
    erc20_abi = '[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]'

    token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)
    return token_contract.functions.decimals().call()
'''from populate_routes import (setup)

def get_ERC20_balance(accountAddress, assetAddress):
    
    Gets and logs the balance of an asset in an account. 
    
    return {} #{assetAddress: balance}

def get_ETH_balance(accountAddress, assetAddress):
'''

