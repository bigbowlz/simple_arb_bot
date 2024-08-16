from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (to_wei)
from trading_env_sims.sim_utilities import (trading_sims_eth_for_erc20)
import json
"""
Simulates regular trader activities on UniswapV2. 
The regular trader account holds ~$15k worth of each baseAsset in the config file.
Every second, the regular trader trades a random baseAsset for another random baseAsset 
for a random value between $300 and $9,000 in a single swap.

Author: ILnaw
Version: 08-14-2024
"""
if __name__ == "__main__":
    regular_trader_erc20_address = '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65' # the regular trader erc20 simulator address
    regular_trader_erc20_key = '0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a'
    regular_trader_erc20_arb_bot = ArbBot(regular_trader_erc20_key)
    
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    base_assets = data["baseAssets"]

    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = regular_trader_erc20_arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = regular_trader_erc20_arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    # Transaction sent by the regular trader address through regular_trader_erc20_arb_bot setup, trading between $300 and $9,000 in a single swap.
    trading_sims_eth_for_erc20(
        regular_trader_erc20_arb_bot, 
        to_wei(0.1, 
        18), 
        to_wei(3, 
        18), 
        end_time, 
        1, 
        sushi_router, 
        base_assets, 
        regular_trader_erc20_address)
    