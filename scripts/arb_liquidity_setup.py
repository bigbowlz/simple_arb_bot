from utilities.trading_utilities import (
    to_wei,
    from_wei,
    send_ETH_to_Arb,
    swap_ETH_for_ERC20,
    send_ERC20,
    wrap_ETH_to_WETH
)
from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (get_account_balances)
import json

'''
arb_liquidity_setup.py

Tests functions of the ArbBot class and the arbitrage contract, and sets up
initial ETH and ERC20 token liquidity in the contract.

Author: ILnaw
Version: 08-14-2024
'''
if __name__ == "__main__":
    arb_bot = ArbBot('0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    pancake_router = arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

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

    # Return all functions of the contract
    print(f'All functions of the arb contract: {arb_bot.bot.all_functions()}')    

    # Send 100 ETH to the arbitrage contract; see if tx_receipt.status returns 1
    # assert send_ETH_to_Arb(arb_bot, 100).status == 1

    # Get the ETH balance of the smart contract
    # balance = arb_bot.web3.eth.get_balance(arb_bot.bot_address)
    # print(f'Current balance of ETH on arb contract: {from_wei(balance, 18)} ETH')
    # assert balance > 99, "Unexpected! Send 100 ETH failed!"

    # Swap 1 ETH for USDT in Uniswap V2
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    for token in data["baseAssets"]:
        token_address = token["address"]
        token_contract = arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        try:
            swap_ETH_for_ERC20(1, arb_bot, token_contract, uniswap_router, arb_bot.bot_address)
        except:
            print("Unexpected! Swap ETH-ERC20 failed!")

    # test getBalance(address) from smart contract and get_balance(address) from arb_bot object
    USDT_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
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
        to_wei(10, 6)) > 0, "Unexpected! Estimated return wrong!"
    
    # test withdrawToken(address), test pending
    # print(f'Withdrawing all USDT balance of {from_wei(usdt_balance, 6)}...')
    # withdraw_receipt = arb_bot.withdraw_token(USDT_address)
    # assert arb_bot.get_balance(USDT_address) == 0, "Unexpected! USDT withdrawal failed"
    # print('All USDT withdrawn')

    # test withdrawETH()
#     print(f'''--------------------------------
# Withdrawing all ETH balance...''')
#     arb_bot.withdraw_eth()
#     test_withdraw_eth_balance = arb_bot.web3.eth.get_balance(arb_bot.bot_address)
#     assert test_withdraw_eth_balance == 0, "Unexpected! ETH withdrawal failed"
#     print(f'Current ETH balance on arb contract: {from_wei(test_withdraw_eth_balance, 18)} ETH')

    # test executeTrade, test pending
    # try:
    #     arb_bot.execute_trade(uniswap_router.address, sushi_router.address, usdc.address, usdt.address, 150)

    # except Exception as e:
    #     print(f"Error while trying to execute arb trade: {e}")
    
    #assert send_ETH_to_Arb(arb_bot, 100).status == 1, "Send ETH to arb failed!"

    # wrap 5 ETH to WETH in sender address
    amount_to_send = to_wei(5, 18)
    assert wrap_ETH_to_WETH(amount_to_send, arb_bot).status == 1, "Wrap ETH to WETH failed!"
    # send 20 WETH to arb_bot
    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_contract = arb_bot.web3.eth.contract(address=weth_address, abi=erc20_abi)
    assert send_ERC20(arb_bot, arb_bot.bot_address, weth_contract, amount_to_send).status == 1, "Send WETH to arb failed!"

    print(f'sender balances: {get_account_balances(arb_bot.web3, arb_bot.sender_address)}')
    print(f'bot balances: {get_account_balances(arb_bot.web3, arb_bot.bot_address)}')

