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
import os
import json

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

def get_account_balances(arb_bot):
#     erc20_abi = '''
#     [
# {
# "constant": true,
# "inputs": [],
# "name": "name",
# "outputs": [
# {
# "name": "",
# "type": "string"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "constant": false,
# "inputs": [
# {
# "name": "_spender",
# "type": "address"
# },
# {
# "name": "_value",
# "type": "uint256"
# }
# ],
# "name": "approve",
# "outputs": [
# {
# "name": "",
# "type": "bool"
# }
# ],
# "payable": false,
# "stateMutability": "nonpayable",
# "type": "function"
# },
# {
# "constant": true,
# "inputs": [],
# "name": "totalSupply",
# "outputs": [
# {
# "name": "",
# "type": "uint256"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "constant": false,
# "inputs": [
# {
# "name": "_from",
# "type": "address"
# },
# {
# "name": "_to",
# "type": "address"
# },
# {
# "name": "_value",
# "type": "uint256"
# }
# ],
# "name": "transferFrom",
# "outputs": [
# {
# "name": "",
# "type": "bool"
# }
# ],
# "payable": false,
# "stateMutability": "nonpayable",
# "type": "function"
# },
# {
# "constant": true,
# "inputs": [],
# "name": "decimals",
# "outputs": [
# {
# "name": "",
# "type": "uint8"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "constant": true,
# "inputs": [
# {
# "name": "_owner",
# "type": "address"
# }
# ],
# "name": "balanceOf",
# "outputs": [
# {
# "name": "balance",
# "type": "uint256"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "constant": true,
# "inputs": [],
# "name": "symbol",
# "outputs": [
# {
# "name": "",
# "type": "string"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "constant": false,
# "inputs": [
# {
# "name": "_to",
# "type": "address"
# },
# {
# "name": "_value",
# "type": "uint256"
# }
# ],
# "name": "transfer",
# "outputs": [
# {
# "name": "",
# "type": "bool"
# }
# ],
# "payable": false,
# "stateMutability": "nonpayable",
# "type": "function"
# },
# {
# "constant": true,
# "inputs": [
# {
# "name": "_owner",
# "type": "address"
# },
# {
# "name": "_spender",
# "type": "address"
# }
# ],
# "name": "allowance",
# "outputs": [
# {
# "name": "",
# "type": "uint256"
# }
# ],
# "payable": false,
# "stateMutability": "view",
# "type": "function"
# },
# {
# "payable": true,
# "stateMutability": "payable",
# "type": "fallback"
# },
# {
# "anonymous": false,
# "inputs": [
# {
# "indexed": true,
# "name": "owner",
# "type": "address"
# },
# {
# "indexed": true,
# "name": "spender",
# "type": "address"
# },
# {
# "indexed": false,
# "name": "value",
# "type": "uint256"
# }
# ],
# "name": "Approval",
# "type": "event"
# },
# {
# "anonymous": false,
# "inputs": [
# {
# "indexed": true,
# "name": "from",
# "type": "address"
# },
# {
# "indexed": true,
# "name": "to",
# "type": "address"
# },
# {
# "indexed": false,
# "name": "value",
# "type": "uint256"
# }
# ],
# "name": "Transfer",
# "type": "event"
# }
# ]
#     '''
#     weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    print(f'ETH - {arb_bot.web3.eth.get_balance(arb_bot.bot_address)}')
    for token in data["baseAssets"]:
        token_address = token["address"]
        print(f'{token["sym"]} - {arb_bot.get_balance(token_address)}')