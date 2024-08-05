'''
arb_liquidity_setup.py

Tests functions of the ArbBot class and the arbitrage contract, and sets up
initial ETH and ERC20 token liquidity in the contract.

Author: ILnaw
Version: 08-04-2024
'''
from web3 import Web3
from utilities.balances import (
    to_wei,
    from_wei,
    sign_and_send_tx
)
from utilities.arb_bot import ArbBot
from utilities.balances import (get_token_decimals, get_account_balances)
from utilities.approve_lp import (approve_tokens)
import os
import json

def send_ETH_to_Arb(arb_bot, amount):
    """
    Sends native ETH from sender account to the arb bot contract. 

    Params:
        arb_bot (ArbBot): an ArbBot contract instance.
        amount (int): Amount in wei.

    Returns:
        tx_receipt (receipt): The receipt of the ETH transfer transaction.
    """
    print('Sending ETH from sender_address to arb contract...')
    # Send ETH to Contract
    tx = {
        'from': arb_bot.sender_address,
        'to': arb_bot.bot_address,
        'value': to_wei(amount, 18), 
        'gas': 400000, 
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'chainId': arb_bot.chain_id
    }

    # Sign and send the transaction
    return sign_and_send_tx(arb_bot.web3, tx, arb_bot.private_key)

def swap_ETH_for_ERC20(arb_bot, weth_instance, ERC20_instance, router_instance):
    """
    Swaps 1 native ETH to USDT on a router, and sends the returned USDT to the arb bot contract. 

    Params:
        arb_bot (ArbBot): an ArbBot contract instance.
        weth_instance (Contract): a contract instance for WETH.
        ERC20_instance (Contract): a contract instance for ERC20.
        router_instance (Contract): a contract instance for the router.

    Returns:
        bool: True for a successful execution of the swap; False otherwise.
    """
    # Define swap parameters
    amount_in_wei = to_wei(1, 18)
    amount_out_min = to_wei(1, 6) 
    path = [weth_instance.address, ERC20_instance.address]
    deadline = int(arb_bot.web3.eth.get_block('latest')['timestamp']) + 300  # 5 minutes from the current block time

    print('''--------------------------------
Wrapping ETH to WETH in sender_address...''')
    # Wrap ETH to WETH
    wrap_tx = weth_instance.functions.deposit().build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'value': amount_in_wei  # Amount of ETH to wrap into WETH
    })

    wrap_tx_receipt = sign_and_send_tx(arb_bot.web3, wrap_tx, arb_bot.private_key)

    if wrap_tx_receipt['status'] == 1:
      print(f"Wrapped {from_wei(weth_instance.functions.balanceOf(arb_bot.sender_address).call(), 18)} WETH on sender address")
    else:
      print('Wrap ETH to WETH failed.')

    print('''--------------------------------
Approving WETH allowance from sender_address to router...''')
    # Approve the Uniswap router to spend WETH
    approve_tx = weth_instance.functions.approve(router_instance.address, amount_in_wei).build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
    })
    WETH_approval_receipt = sign_and_send_tx(arb_bot.web3, approve_tx, arb_bot.private_key)

    if WETH_approval_receipt['status'] == 1:
      print(f"Current WETH allowance on router: {from_wei(weth_instance.functions.allowance(arb_bot.sender_address, router_instance.address).call(), 18)} WETH")
    else:
      print('WETH approval failed.')

    print(f'''--------------------------------
Swapping WETH on sender_address to {ERC20_instance.functions.symbol().call()} on arb contract...''')
    # Perform the swap
    swap_tx = router_instance.functions.swapExactETHForTokens(
        amount_out_min,
        path,
        arb_bot.bot_address,
        deadline
    ).build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'value': amount_in_wei,  # Amount of WETH to swap
    })

    swap_receipt = sign_and_send_tx(arb_bot.web3, swap_tx, arb_bot.private_key)

    print(f"Current USDT balance on arb contract: {from_wei(arb_bot.bot.functions.getBalance(ERC20_instance.address).call(), 6)} USDT")
    return swap_receipt['status']

def read_all_functions(arb_bot):
    """
    Reads all solidity functions of the arb bot contract. 

    Params:
        arb_bot (ArbBot): an ArbBot contract instance.
    
    Returns:
        none
    """
    print(f'All functions of the arb contract: {arb_bot.bot.all_functions()}')    

if __name__ == "__main__":
    arb_bot = ArbBot(5, 5, '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    pancake_router = arb_bot.web3.eth.contract(address=pancake_router_address, abi=uniswap_router_abi)

    erc20_abi = '''
    [
{
"constant": true,
"inputs": [],
"name": "name",
"outputs": [
{
"name": "",
"type": "string"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"constant": false,
"inputs": [
{
"name": "_spender",
"type": "address"
},
{
"name": "_value",
"type": "uint256"
}
],
"name": "approve",
"outputs": [
{
"name": "",
"type": "bool"
}
],
"payable": false,
"stateMutability": "nonpayable",
"type": "function"
},
{
"constant": true,
"inputs": [],
"name": "totalSupply",
"outputs": [
{
"name": "",
"type": "uint256"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"constant": false,
"inputs": [
{
"name": "_from",
"type": "address"
},
{
"name": "_to",
"type": "address"
},
{
"name": "_value",
"type": "uint256"
}
],
"name": "transferFrom",
"outputs": [
{
"name": "",
"type": "bool"
}
],
"payable": false,
"stateMutability": "nonpayable",
"type": "function"
},
{
"constant": true,
"inputs": [],
"name": "decimals",
"outputs": [
{
"name": "",
"type": "uint8"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"constant": true,
"inputs": [
{
"name": "_owner",
"type": "address"
}
],
"name": "balanceOf",
"outputs": [
{
"name": "balance",
"type": "uint256"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"constant": true,
"inputs": [],
"name": "symbol",
"outputs": [
{
"name": "",
"type": "string"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"constant": false,
"inputs": [
{
"name": "_to",
"type": "address"
},
{
"name": "_value",
"type": "uint256"
}
],
"name": "transfer",
"outputs": [
{
"name": "",
"type": "bool"
}
],
"payable": false,
"stateMutability": "nonpayable",
"type": "function"
},
{
"constant": true,
"inputs": [
{
"name": "_owner",
"type": "address"
},
{
"name": "_spender",
"type": "address"
}
],
"name": "allowance",
"outputs": [
{
"name": "",
"type": "uint256"
}
],
"payable": false,
"stateMutability": "view",
"type": "function"
},
{
"payable": true,
"stateMutability": "payable",
"type": "fallback"
},
{
"anonymous": false,
"inputs": [
{
"indexed": true,
"name": "owner",
"type": "address"
},
{
"indexed": true,
"name": "spender",
"type": "address"
},
{
"indexed": false,
"name": "value",
"type": "uint256"
}
],
"name": "Approval",
"type": "event"
},
{
"anonymous": false,
"inputs": [
{
"indexed": true,
"name": "from",
"type": "address"
},
{
"indexed": true,
"name": "to",
"type": "address"
},
{
"indexed": false,
"name": "value",
"type": "uint256"
}
],
"name": "Transfer",
"type": "event"
}
]
    '''
    USDC_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    usdc = arb_bot.web3.eth.contract(address=USDC_address, abi=erc20_abi)

    USDT_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    usdt = arb_bot.web3.eth.contract(address=USDT_address, abi=erc20_abi)

    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
    weth = arb_bot.web3.eth.contract(address=weth_address, abi=weth_abi)

    # Return all functions of the contract
    read_all_functions(arb_bot)

    # Send 100 ETH to the arbitrage contract; see if tx_receipt.status returns 1
    assert send_ETH_to_Arb(arb_bot, 100).status == 1

    # Get the ETH balance of the smart contract
    balance = arb_bot.web3.eth.get_balance(arb_bot.bot_address)
    print(f'Current balance of ETH on arb contract: {from_wei(balance, 18)} ETH')
    assert balance > 99, "Unexpected! Send 100 ETH failed!"

    # Swap 1 ETH for USDT in Uniswap V2
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    for token in data["baseAssets"]:
        token_address = token["address"]
        token_contract = arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        assert swap_ETH_for_ERC20(arb_bot, weth, token_contract, uniswap_router) == 1, "Unexpected! Swap WETH-ERC20 failed!"

    # test getBalance(address) from smart contract and get_balance(address) from arb_bot object
    usdt_balance = arb_bot.get_balance(USDT_address)
    if usdt_balance == 3139017495:
      print(f'''--------------------------------
getBalance(address) test succeeded''')

    # test owner()
    assert arb_bot.get_owner()==arb_bot.sender_address, "Unexpected! owner() test failed"

    # test estimateTradeReturn(address,address,address,address,uint256)
    assert arb_bot.estimate_return(
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", 
        "0xEfF92A263d31888d860bD50809A8D171709b7b1c", 
        "0xdAC17F958D2ee523a2206206994597C13D831ec7", 
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 
        to_wei(10, 6)) == 6412564, "Unexpected! Estimated return wrong!"
    
    get_account_balances(arb_bot)

    # test withdrawToken(address), STILL DOESN'T WORK
    # print(f'Withdrawing all USDT balance of {from_wei(usdt_balance, 6)}...')
    # withdraw_receipt = arb_bot.withdraw_token(USDT_address)
    # assert arb_bot.get_balance(USDT_address) == 0, "Unexpected! USDT withdrawal failed"
    # print('All USDT withdrawn')

    # test withdrawETH()
    print(f'''--------------------------------
Withdrawing all ETH balance...''')
    arb_bot.withdraw_eth()
    test_withdraw_eth_balance = arb_bot.web3.eth.get_balance(arb_bot.bot_address)
    assert test_withdraw_eth_balance == 0, "Unexpected! ETH withdrawal failed"
    print(f'Current balance of ETH on arb contract: {from_wei(test_withdraw_eth_balance, 18)} ETH')

    try:
        arb_bot.execute_trade(uniswap_router.address, pancake_router.address, usdc.address, usdt.address, 150)

    except Exception as e:
        print(f"Error while trying to execute arb trade: {e}")
       