from utilities.populate_routes import (setup)
from utilities.arb_bot import ArbBot
import json
import time
import csv
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

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
        uniswap_v2_pair_abi (str): abi of a uniswap v2 pair contract.
        factory_abi (str): abi of a uniswap v2 factory contract.
        tokenA_address (str): address of a token contract.
        tokenB_address (str): address of a token contract.
        router1 (Contract): Contract instance of a router.
        router2 (Contract): Contract instance of a router.
    
    Returns:
        (float): price difference of the same pair of token on two different routers. 
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

    reserves_on_2 = pair_contract_2.functions.getReserves().call()
    reserve0_on_2, reserve1_on_2, _ = reserves_on_2
    price_on_router2 = reserve0_on_2 / reserve1_on_2
    
    return (price_on_router2 - price_on_router1)/price_on_router1

def get_pair_contract(web3, factory_contract, pair_contract_abi, token1_address, token2_address):
    """
    Get the pair contract of two tokens on an AMM dex through its factory contract.

    Params:
        web3 (Provider): A Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
        factory_contract (Contract): Contract instance of a factory in an AMM.
        pair_contract_abi (str): abi of a uniswap v2 pair contract.
        token1_address (str): address of a token contract.
        token2_address (str): address of a token contract.

    Returns:
        (Contract): the pair contract of two tokens on an AMM.
    """
    pair_contract_address = factory_contract.functions.getPair(token1_address, token2_address).call()
    return web3.eth.contract(address = pair_contract_address, abi = pair_contract_abi)

def hit_profit_target(min_profitBP, slippage_bufferBP, trading_feeBP, price_diff):
    """
    Determines whether the price difference of a token pair on different routers hit the profit target based on 
    minimum profitability, slippage buffer, and trading fee configs.

    Params:
        min_profitBP (int): Basis point value of the minimum profitability accepted in a trade that's smaller than profit/(liquidity + gas).
        slippage_bufferBP (int): Basis point value of the slippage buffer percentage added for swaps.
        trading_feeBP (int): Basis point value of the total trading fees involved in the arb trade. 
        price_diff (float): price difference of the same pair of token on two different routers.  

    Returns:
        (bool): true if the price difference hits the profit target; false otherwise.
    """
    if price_diff > (min_profitBP + slippage_bufferBP + trading_feeBP)/100:  
        return True
    return False

if __name__ == "__main__":
    '''
    The main function that serves as the entry point of the program.
    '''
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    min_profitBP = arb_bot_config["min_profitBP"]
    slippage_bufferBP = arb_bot_config["slippage_bufferBP"]
    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    PRIVATE_KEY = arb_bot_config["PRIVATE_KEY"]
    arb_bot = ArbBot(min_profitBP, slippage_bufferBP, PRIVATE_KEY)

    web3, data, api_key, api_url = setup()

    # create UniswapV2Router instance
    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    # create PancakeRouter instance
    pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    pancake_router = arb_bot.web3.eth.contract(address=pancake_router_address, abi=uniswap_router_abi)

    # create Router contract dict
    router_dict = {uniswap_router_address: uniswap_router, pancake_router_address: pancake_router}
    # load Uniswap Factory abi
    with open("configs/factory_ABIs/UniswapV2Factory_abi.json", "r") as factory_abi_file:
        factory_abi = json.load(factory_abi_file)
        print("factory_abi read from json file.")

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

    # Create a csv file to track trade txs and performance.
    with open("performance_monitor/trade_logs_bot.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "price_diff", 
            "time_opportunity_found", 
            "time_tx_init", 
            "time_tx_finalized", 
            "amount_in", 
            "amount_out", 
            "txhash"
            ])
    
    # Run the bot for the specified duration
    print("Bot setup complete. Monitoring on-chain opportunites...")
    while time.time() - start_time < duration:
	    for viable_route in data["routes"]:
             token1 = viable_route["token1"]
             token2 = viable_route["token2"]
             router1 = router_dict[viable_route["router1"]]
             router2 = router_dict[viable_route["router2"]]

             price_diff = get_price_diff(
                 web3,
                 uniswap_v2_pair_abi,
                 factory_abi,
                 token1,
                 token2,
                 router1,
                 router2
                 )

             if hit_profit_target(min_profitBP, slippage_bufferBP, 60, price_diff) == True:
                 time_opportunity_found = time.time()
                 token1_balance = arb_bot.get_balance(token1)
                 if arb_bot.estimate_return(router1, router2, token1, token2) > token1_balance:
                    time_tx_init = time.time()
                    txhash = arb_bot.executeTrade(router1, router2, token1, token2, token1_balance)
                    time_tx_finalized = time.time()
                 elif arb_bot.estimate_return(router2, router1, token1, token2) > token1_balance:
                    txhash = arb_bot.executeTrade(router2, router1, token1, token2, token1_balance)

                 # Write trade performance data into the csv file each time a dual-dex trade tx is initiated.
                 with open("performance_monitor/trade_logs_bot.csv", mode='a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([
                         price_diff, 
                         time_opportunity_found, 
                         time_tx_init, 
                         time_tx_finalized, 
                         token1_balance, # balance before the trade
                         arb_bot.get_balance(token1), # balance after the trade
                         txhash
                         ])
             # Sleep for a short duration to avoid busy-waiting in CPU
             time.sleep(1)
    print(f"Completed bot operations for {int(duration/60)} minutes.")

