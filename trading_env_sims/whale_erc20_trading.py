from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (to_wei)
from trading_env_sims.sim_utilities import (trading_sims_erc20_for_erc20)
import json
"""
Simulates whale trader activities on UniswapV2. 
The whale account holds ~$300k worth of each baseAsset in the config file.
Every 5 seconds, the whale trades a random baseAsset for another random baseAsset 
for a random value between $30,000 and $100,000 in a single swap.

Author: ILnaw
Version: 08-14-2024
"""
if __name__ == "__main__":
    whale_erc20_address = '0x90F79bf6EB2c4f870365E785982E1f101E93b906' # the whale erc20 simulator address
    whale_erc20_private_key = '0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6' # private key of the whale_erc20 simulator address
    whale_erc20_arb_bot = ArbBot(whale_erc20_private_key)
    
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    base_assets = data["baseAssets"]
    
    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = whale_erc20_arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = whale_erc20_arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    trading_sims_erc20_for_erc20(
        whale_erc20_arb_bot, 
        to_wei(30_000, 6), 
        to_wei(100_000, 6), 
        end_time, 
        5, 
        uniswap_router, 
        base_assets, 
        whale_erc20_address)
    