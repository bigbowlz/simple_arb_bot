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
Version: 08-14-2024
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
#     print(f'''router1 liquidity: 
# reserve0 - {reserve0_on_1}
# reserve1 - {reserve1_on_1}''')
    price_on_router1 = reserve0_on_1 / reserve1_on_1

    reserves_on_2 = pair_contract_2.functions.getReserves().call()
    reserve0_on_2, reserve1_on_2, _ = reserves_on_2
#     print(f'''router2 liquidity: 
# reserve0 - {reserve0_on_2}
# reserve1 - {reserve1_on_2}''')
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
    arb_bot = ArbBot(PRIVATE_KEY, min_profitBP = min_profitBP, slippage_bufferBP = slippage_bufferBP)

    web3, data, api_key, api_url = setup()

    # create UniswapV2Router instance
    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    # create SushiRouter instance
    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    # create Router contract dict
    router_dict = {uniswap_router_address: uniswap_router, sushi_router_address: sushi_router}
    
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
            "base_asset",
            "intermediate_asset",
            "first_swap_router",
            "second_swap_router",
            "base_asset_balance_before_swap", 
            "base_asset_balance_after_swap", 
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
                 print(f'''Profit target hit! 
Price diff is now {price_diff*100}% 
for {token1} and {token2}
between Uniswap and Sushi.''')
                 time_opportunity_found = time.time()
                 token1_balance = arb_bot.get_balance(token1)
                 time_tx_init = "estimate_return below amount_in."
                 time_tx_finalized = "executeTrade failed"
                 txhash = "executeTrade failed"
                 router_1 = "N/A"
                 router_2 = "N/A"
                 # determine sequence of trading venues through if else statements
                 trade_router1_then_router2 = arb_bot.estimate_return(router1.address, router2.address, token1, token2, token1_balance)
                 print(f"amount difference after trading on router1 then router2: {trade_router1_then_router2 - token1_balance}")
                 trade_router2_then_router1 = arb_bot.estimate_return(router2.address, router1.address, token1, token2, token1_balance)
                 print(f"amount difference after trading on router2 then router1: {trade_router2_then_router1 - token1_balance}")
                 if trade_router1_then_router2 > token1_balance:
                    router_1 = router1.address
                    router_2 = router2.address
                    time_tx_init = time.time()
                    txhash = arb_bot.executeTrade(router1.address, router2.address, token1, token2, token1_balance)
                    time_tx_finalized = time.time()
                 elif trade_router2_then_router1 > token1_balance:
                    router_1 = router2.address
                    router_2 = router1.address
                    time_tx_init = time.time()
                    txhash = arb_bot.executeTrade(router2.address, router1.address, token1, token2, token1_balance)
                    time_tx_finalized = time.time()

                 # Write trade performance data into the csv file each time a dual-dex trade tx is initiated.
                 with open("performance_monitor/trade_logs_bot.csv", mode='a', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow([
                         price_diff, 
                         time_opportunity_found, 
                         time_tx_init, 
                         time_tx_finalized, 
                         token1,
                         token2,
                         router_1,
                         router_2,
                         token1_balance, # balance before the trade
                         arb_bot.get_balance(token1), # balance after the trade
                         txhash
                         ])
             # Sleep for a short duration to avoid busy-waiting in CPU
             time.sleep(1)
    print(f"Completed bot operations for {int(duration/60)} minutes.")

