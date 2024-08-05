from utilities.populate_routes import (populate_routes)
from web3 import Web3
from utilities.arb_bot import ArbBot
from utilities.populate_routes import (setup)
import json
'''
trade.py

Searches routes for trade opportunities and determine profitability. 
Executes trades when profit target is hit, and logs results to console.

Author: ILnaw
Version: 0.0.1
'''
def get_price_diff(web3, uniswap_v2_pair_abi, factory_abi, tokenA_address, tokenB_address, router1, router2):
    """
    Get the price difference of tokenA/tokenB on two different routers.
    """
    # create Factory instance
    factory1_address = router1.functions.factory().call()
    factory1 = web3.eth.contract(address=factory1_address, abi=factory_abi)
    factory2_address = router2.functions.factory().call()
    factory2 = web3.eth.contract(address=factory2_address, abi=factory_abi)

    pair_contract_1 = get_pair_contract(web3, factory1, uniswap_v2_pair_abi, tokenA_address, tokenB_address)
    pair_contract_2 = get_pair_contract(web3, factory2, uniswap_v2_pair_abi, tokenA_address, tokenB_address)

    # Fetch reserves
    reserves_on_1 = pair_contract_1.functions.getReserves().call()
    reserve0_on_1, reserve1_on_1, _ = reserves_on_1
    price_on_router1 = reserve0_on_1 / reserve1_on_1

    reserves_on_2 = pair_contract_1.functions.getReserves().call()
    reserve0_on_2, reserve1_on_2, _ = reserves_on_2
    price_on_router1 = reserve0_on_2 / reserve1_on_2
    
    return (price_on_router1 - price_on_router1)/price_on_router1

def get_pair_contract(web3, factory_contract, pair_contract_abi, token1_address, token2_address):
    pair_contract_address = factory_contract.functions.getPair(token1_address, token2_address).call()
    return web3.eth.contract(pair_contract_address, pair_contract_abi)

def hit_profit_target(min_profitBP, slippage_bufferBP, price_diff):
    if price_diff > min_profitBP + slippage_bufferBP + 0.006:  
        return True
    return False



def main():
    '''
    The main function that serves as the entry point of the program.
    '''
    web3, data, api_key, api_url = setup()
    populate_routes(data, web3)

    # Initiate the arb bot instance
    print('Initiating the arbitrage bot...')
    min_profitBP = input("Provide the min profitability target in bps of your bot:")
    slippage_bufferBP = input("Provide the slippage buffer in bps of your bot:")
    arb_bot = ArbBot(min_profitBP, slippage_bufferBP, '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')

    # create UniswapV2Router instance
    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    # create PancakeRouter instance
    pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    pancake_router = arb_bot.web3.eth.contract(address=pancake_router_address, abi=uniswap_router_abi)

    # create Uniswap Factory instance
    uniswap_factory_address = uniswap_router.functions.factory().call()
    with open("configs/factory_ABIs/UniswapV2Factory_abi.json", "r") as factory_abi_file:
        factory_abi = json.load(factory_abi_file)
        print("factory_abi read from json file.")
    uniswap_factory = web3.eth.contract(address=uniswap_factory_address, abi=factory_abi)
    


    uniswap_v2_pair_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "getReserves",
            "outputs": [
                {"name": "_reserve0", "type": "uint112"},
                {"name": "_reserve1", "type": "uint112"},
                {"name": "_blockTimestampLast", "type": "uint32"},
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        }
    ]

    while True: # to be changed to run for 2 hours
	    for viable_route in data["routes"]:
    	    if hit_profit_target(min_profitBP, slippage_bufferBP, price_diff) == True:
		        executeTrade(viable_route, amount_in)
		        
