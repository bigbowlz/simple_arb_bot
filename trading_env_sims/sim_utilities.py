from scripts.arb_liquidity_setup import (swap_ETH_for_ERC20)
from utilities.trading_utilities import (get_account_balances, to_wei, swap_ERC20_for_ERC20, get_estimated_return, approve_tokens, wrap_ETH_to_WETH, from_wei)
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
def trading_sims_eth_for_erc20(
        arb_bot, 
        eth_lower_bound, 
        eth_upper_bound, 
        end_time, 
        interval, 
        router_instance, 
        base_assets, 
        recipient_address):
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
            "tx_receipt"
            ])
    with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
        erc20_abi = json.load(erc20_abi_file)
        
    while time.time() < end_time:
        random_asset_index = random.randint(0, len(base_assets)-1)        
        asset_address = base_assets[random_asset_index]["address"]
        asset_contract = arb_bot.web3.eth.contract(address=asset_address, abi=erc20_abi)

        # Swap a random value within the trade bound of ETH for the base asset.
        random_ETH_value_in_wei = random.randint(eth_lower_bound, eth_upper_bound)
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
                    "ETH", 
                    random_ETH_value_in_wei, 
                    asset_address, 
                    swap_receipt
                    ])
        except Exception:
            print(f"Swap failed from ETH to {asset_contract.functions.symbol().call()}.")
        
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

def trading_sims_erc20_for_erc20(
        arb_bot, 
        erc20_lower_bound, 
        erc20_upper_bound, 
        end_time, 
        interval, 
        router_instance, 
        base_assets, 
        recipient_address):
    """
    Simulates trading activities at fixed intervals until end time is reached. 
    
    Randomly finds a baseAsset and trades it with a random value for another random baseAsset as long as the two assets are not the same. 
    Trade transactions are recorded in a csv file.

    Params:
        arb_bot (ArbBot): an ArbBot instance.
        erc20_lower_bound (int): the lower bound of the trade size in wei.
        erc20_upper_bound (int): the upper bound of the trade size in wei.
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
            "tx_receipt"
            ])
    with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
        erc20_abi = json.load(erc20_abi_file)

    while time.time() < end_time:
        random_asset_1_index = random.randint(0, len(base_assets)-1)
        random_asset_2_index = random.randint(0, len(base_assets)-1)
        if random_asset_1_index == random_asset_2_index:
            continue # cannot trade the asset for itself
        
        asset_1_address = base_assets[random_asset_1_index]["address"]
        asset_2_address = base_assets[random_asset_2_index]["address"]        
        asset_1_contract = arb_bot.web3.eth.contract(address=asset_1_address, abi=erc20_abi)
        asset_2_contract = arb_bot.web3.eth.contract(address=asset_2_address, abi=erc20_abi)

        usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        
        # Swap a random value within the trade bound of asset_1 for asset_2.
        random_USDT_wei_value = random.randint(erc20_lower_bound, erc20_upper_bound)
        if asset_1_address == usdt_address:
            amount_in_wei = random_USDT_wei_value
        else: # as long as asset_1 is not USDT, estimate the random USDT equivalent value of asset_1
            amount_in_wei = get_estimated_return(
                arb_bot.web3, 
                router_instance, 
                random_USDT_wei_value, 
                token_in=usdt_address, 
                token_out=asset_1_address 
                )
            
        if isinstance(amount_in_wei, int):
            print(f"Trying to trade {base_assets[random_asset_1_index]["sym"]} for {base_assets[random_asset_2_index]["sym"]} with {amount_in_wei} in value.")
            try:
                swap_receipt = swap_ERC20_for_ERC20(
                    amount_in_wei, 
                    arb_bot, 
                    asset_1_address, 
                    asset_2_address, 
                    router_instance, 
                    recipient_address)
                if swap_receipt['status'] == 1:
                        print(f'''Account balances:
    {get_account_balances(arb_bot.web3, recipient_address)}
    ''') 
                with open("trading_env_sims/" + recipient_address+ ".csv", mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        time.time(),
                        asset_1_address, 
                        amount_in_wei, 
                        asset_2_address, 
                        swap_receipt
                    ])
            except Exception as e:
                print(f'''Swap failed!
{e}
''')
        time.sleep(interval)
