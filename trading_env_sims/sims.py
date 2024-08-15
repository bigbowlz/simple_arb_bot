from scripts.arb_liquidity_setup import (swap_ETH_for_ERC20)
from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (get_account_balances, to_wei, get_estimated_return, approve_tokens, send_ERC20, swap_ERC20_for_ERC20)
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
def trading_sims(arb_bot, trade_lower_bound, trade_upper_bound, end_time, interval, router_instance, base_assets, recipient_address):
    """
    Simulates trading activities at fixed intervals until end time is reached. 
    
    Randomly finds a baseAsset and trades it with a random value for another random baseAsset as long as the two assets are not the same. 
    Trade transactions are recorded in a csv file.

    Params:
        arb_bot (ArbBot): an ArbBot instance.
        trade_lower_bound (int): the lower bound of the trade size in USDT.
        trade_upper_bound (int): the upper bound of the trade size in USDT.
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

    while time.time() < end_time:
        random_asset_1_index = random.randint(0, len(base_assets)-1)
        random_asset_2_index = random.randint(0, len(base_assets)-1)
        if random_asset_1_index == random_asset_2_index:
            continue
        
        asset_1_address = base_assets[random_asset_1_index]["address"]
        asset_2_address = base_assets[random_asset_2_index]["address"]        
        usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        
        # Swap a random value within the trade bound of asset_1 for asset_2.
        random_USDT_value = random.randint(trade_lower_bound, trade_upper_bound)
        print(f"Trading value: {random_USDT_value}")
        if asset_1_address == usdt_address:
            amount_in_wei = to_wei(random_USDT_value, 6)
        else:
            amount_in_wei = get_estimated_return(
                arb_bot.web3, 
                router_instance, 
                random_USDT_value, 
                token_in=usdt_address, 
                token_out=asset_1_address
                )
            
        if isinstance(amount_in_wei, int):
            print(f"Trying to trade {base_assets[random_asset_1_index]["sym"]} for {base_assets[random_asset_2_index]["sym"]} with {amount_in_wei} in value.")
            try:
                swap_receipt = swap_ERC20_for_ERC20(amount_in_wei, arb_bot, asset_1_address, asset_2_address, router_instance, recipient_address)
                if swap_receipt['status'] == 1:
                        print(f'''
    Account balances:
    {get_account_balances(arb_bot.web3, recipient_address)}
    ''') 
                with open("trading_env_sims/" + recipient_address+ ".csv", mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        time.time(),
                        asset_1_address, 
                        amount_in_wei, 
                        asset_2_address, 
                        swap_receipt.transactionHash.hex()
                    ])
            except Exception as e:
                print(f"Swap failed with {str(e)}")
            
        time.sleep(interval)
 
def setup_sim_account(base_assets, erc20_abi, amount_from_wei, arb_bot, weth, router, recipient_address):
    """
    Sets up simulation account with 100 ETH worth of value for each baseAsset as specified in the config file.

    Params:
        base_assets (list): a list of base assets for trading.
        erc20_abi (str): the abi file for the erc20 token.
        amount_from_wei (int): amount of token to fund, converted from wei.
        arb_bot (ArbBot): an ArbBot instance. 
        weth (Contract): Contract instance for the WETH token.
        router (Contract): Contract instance for the router for trading base assets.
        recipient_address: Recipient address of the returned base assets.

    Returns:
        balances (dict): balances of all tokens in a dictionary.
    """
    btc_iCAN_address = '0x49AeF2C4005Bf572665b09014A563B5b9E46Df21'
    btc_iCAN_contract = arb_bot.web3.eth.contract(address=btc_iCAN_address, abi=erc20_abi)

    usdc_iCAN_address = '0xa9efDEf197130B945462163a0B852019BA529a66'
    usdc_iCAN_contract = arb_bot.web3.eth.contract(address=usdc_iCAN_address, abi=erc20_abi)

    send_ERC20(ArbBot("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"), recipient_address, btc_iCAN_contract, to_wei(50, 8))
    send_ERC20(ArbBot("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"), recipient_address, usdc_iCAN_contract, to_wei(50, 6))
    unlimited_allowance = arb_bot.web3.to_wei(2**256 - 1, 'wei')

    # For every base asset, try to trade the same amount of ETH for the asset, and approve unlimited allowance of the asset on router. 
    for token in base_assets:
        token_address = token["address"]
        token_contract = arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        assert swap_ETH_for_ERC20(amount_from_wei, arb_bot, weth, token_contract, router, recipient_address) == 1, "Unexpected! Swap WETH-ERC20 failed!"
        approve_tokens(arb_bot.web3, token_contract, router.address, unlimited_allowance, arb_bot.private_key)
    return get_account_balances(arb_bot.web3, recipient_address)

if __name__ == "__main__":
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(whale_private_key)

    regular_trader_address = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
    regular_trader_key = '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a'
    regular_trader_arb_bot = ArbBot(regular_trader_key)
    
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    print("Data read from json file.")
    base_assets = data["baseAssets"]

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

    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
        uniswap_router_abi = json.load(file)
    uniswap_router = whale_arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
    weth = whale_arb_bot.web3.eth.contract(address=weth_address, abi=weth_abi)
    

    # whale trader holds ~$600k worth of each asset in account
    print("Setting up whale account...")
    print(f'''
    Whale account balances:
    {setup_sim_account(base_assets, erc20_abi, 200, whale_arb_bot, weth, uniswap_router, whale_address)}
    ''') 

    # regular trader holds ~$15k worth of each asset in account
    print("Setting up regular trader account...")
    print(f'''
    Regular trader account balances:
    {setup_sim_account(base_assets, erc20_abi, 5, regular_trader_arb_bot, weth, uniswap_router, regular_trader_address)}
    ''') 

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    # Transaction sent by the whale address through whale_arb_bot setup, trading between $5,000 and $100,000 in a single swap.
    trading_sims(whale_arb_bot, 5 * 10 ** 3, 100 * 10 ** 3, end_time, 30, uniswap_router, base_assets, whale_address)

    # Transaction sent by the whale address through whale_arb_bot setup, trading between $11 and $5,000 in a single swap.
    trading_sims(regular_trader_arb_bot, 11, 5 * 10 ** 3, end_time, 30, uniswap_router, base_assets, regular_trader_address)
