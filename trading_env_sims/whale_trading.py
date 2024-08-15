from utilities.arb_bot import ArbBot
from sims_eth_for_erc20 import (trading_sims)
import json
"""
Simulates whale trader activities on UniswapV2. 
The whale account holds ~$300k worth of each baseAsset in the config file.
Every 10 seconds, the whale trades a random baseAsset for another random baseAsset 
for a random value between $20,000 and $50,000 in a single swap.

Author: ILnaw
Version: 08-14-2024
"""
if __name__ == "__main__":
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(whale_private_key)
    
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    base_assets = data["baseAssets"]

    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = whale_arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = whale_arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    # Transaction sent by the whale address through whale_arb_bot setup, trading between $50,000 and $100,000 in a single swap.
    trading_sims(whale_arb_bot, 10_000, 1_000_000, end_time, 5, uniswap_router, base_assets, whale_address)