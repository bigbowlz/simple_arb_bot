from scripts.arb_liquidity_setup import (swap_ETH_for_ERC20)
from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (get_account_balances, to_wei, approve_tokens, wrap_ETH_to_WETH, from_wei)
import json
import time
import random
import csv
'''
sims.py

Includes functions to set up simulation trader accounts and to start trading simulation.

Author: ILnaw
Version: 08-14-2024
'''
def trading_sims(arb_bot, eth_lower_bound, eth_upper_bound, end_time, interval, router_instance, base_assets, recipient_address):
    """
    Simulates trading activities at fixed intervals until end time is reached. 
    
    Randomly finds a baseAsset and trades ETH with a random value for the baseAsset. 
    Trade transactions are recorded in a csv file.

    Params:
        arb_bot (ArbBot): an ArbBot instance.
        eth_lower_bound (int): the lower bound of the ETH trade size in wei.
        eth_upper_bound (int): the upper bound of the ETH trade size in wei.
        end_time (float): the end_time of the balancing logging.
        interval (int): the interval of logging in seconds.
        router_instance (Contract): a contract instance for the router.
        base_assets (list): the list of base assets that can be traded in.
        recipient_address (str): the address of the recipient. 
    """
    with open("trading_env_sims/" + recipient_address+ ".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", 
            "token_in", 
            "amount_in", 
            "token_out", 
            "txhash"
            ])
    with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
        erc20_abi = json.load(erc20_abi_file)
        
    while time.time() < end_time:
        random_asset_index = random.randint(0, len(base_assets)-1)        
        asset_address = base_assets[random_asset_index]["address"]
        asset_contract = arb_bot.web3.eth.contract(address=asset_address, abi=erc20_abi)

        # Swap a random value within the trade bound of ETH for the base asset.
        random_ETH_value_in_wei = to_wei(random.randint(eth_lower_bound, eth_upper_bound), 18)
        print(f"Trying to trade ETH for {base_assets[random_asset_index]["sym"]} with {random_ETH_value_in_wei} wei in value.")
        try:
            swap_receipt = swap_ETH_for_ERC20(from_wei(random_ETH_value_in_wei, 18), arb_bot, asset_contract, router_instance, recipient_address)
            if swap_receipt['status'] == 1:
                    print(f'''
    Account balances:
    {get_account_balances(arb_bot.web3, recipient_address)}
    ''') 
            with open("trading_env_sims/" + recipient_address+ ".csv", mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    time.time(),
                    asset_address, 
                    random_ETH_value_in_wei, 
                    asset_address, 
                    swap_receipt.transactionHash.hex()
                ])
        except Exception as e:
            print(f"Swap failed with {str(e)}")
        
        time.sleep(interval)
 
def setup_sim_account(base_assets, erc20_abi, amount_from_wei, arb_bot, router, recipient_address):
    """
    Sets up simulation account with 100 ETH worth of value for each baseAsset as specified in the config file.

    Params:
        base_assets (list): a list of base assets for trading.
        erc20_abi (str): the abi file for the erc20 token.
        amount_from_wei (int): amount of token to fund, converted from wei.
        arb_bot (ArbBot): an ArbBot instance. 
        router (Contract): Contract instance for the router for trading base assets.
        recipient_address: Recipient address of the returned base assets.

    Returns:
        balances (dict): balances of all tokens in a dictionary.
    """
    # btc_iCAN_address = '0x49AeF2C4005Bf572665b09014A563B5b9E46Df21'
    # btc_iCAN_contract = arb_bot.web3.eth.contract(address=btc_iCAN_address, abi=erc20_abi)

    # usdc_iCAN_address = '0xa9efDEf197130B945462163a0B852019BA529a66'
    # usdc_iCAN_contract = arb_bot.web3.eth.contract(address=usdc_iCAN_address, abi=erc20_abi)

    # send_ERC20(ArbBot("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"), recipient_address, btc_iCAN_contract, to_wei(50, 8))
    # send_ERC20(ArbBot("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"), recipient_address, usdc_iCAN_contract, to_wei(50, 6))
    
    # fund recipient with WETH
    try:
        wrap_ETH_to_WETH(to_wei(amount_from_wei, 18), arb_bot)
    except:
        print("Wrap ETH failed.")
        
    unlimited_allowance = arb_bot.web3.to_wei(2**256 - 1, 'wei')

    # For every base asset, try to trade the same amount of ETH for the asset, and approve unlimited allowance of the asset on router. 
    for token in base_assets:
        token_address = token["address"]
        token_contract = arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        try:
            swap_ETH_for_ERC20(amount_from_wei, arb_bot, token_contract, router, recipient_address) == 1
            approve_tokens(arb_bot.web3, token_contract, router.address, unlimited_allowance, arb_bot.private_key)
        except:
            print("Swap ETH-ERC20 failed, may due to swapping ETH for WETH.")
    return get_account_balances(arb_bot.web3, recipient_address)