from scripts.arb_liquidity_setup import (swap_ETH_for_ERC20, swap_WETH_for_ERC20)
from utilities.arb_bot import ArbBot
from utilities.balances import (get_account_balances)
import json
import time
import random
'''
sims.py

Simulates trading activities in routers based on two different types of traders: 
    - regular traders
    - whale traders

Trading activities are fixed interval-based.    
'''
def get_estimated_return(web3, router_instance, amount_in, token_in, token_out):
    """
    Gets the estimated trade return when trading in a specified amount of a token for another on a router.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        router_instance (Contract): a contract instance for the router.
        amount_in (int): the amount in wei to be traded in.
        token_in (str): the address of the token to be traded in.
        token_out (str): the address of the trade return token.

    Returns:
        amounts_out (int): the value of the return token in wei.
    """
    # Convert the amount to the correct units (e.g., from ETH to wei)
    amount_in_wei = web3.to_wei(amount_in, 'ether')
    
    # Call the `getAmountsOut` function
    amounts_out = router_instance.functions.getAmountsOut(
        amount_in_wei,
        [token_in, token_out]
    ).call()
    
    return amounts_out # returns the amount in wei
    
def whale_trading_sims(arb_bot, end_time, interval, router_instance, base_assets, recipient_address):
    """
    Simulates whale trading activities at fixed intervals until end time is reached.
    """
    while time.time() < end_time:
        # For every base asset, try to equivalent worth of the asset in address 2.
        for token in base_assets:
            token_address = token["address"]
            if token_address == "0xdAC17F958D2ee523a2206206994597C13D831ec7":
                continue
            else:
                random_USDT_value = random.randint(10, 600)*1000 # limit trade size within the $10k to $600k range
                amount_in_wei = get_estimated_return(arb_bot.web3, router_instance, random_USDT_value, "0xdAC17F958D2ee523a2206206994597C13D831ec7", token_address)
                if isinstance(amount_in_wei, int):
                    swap_WETH_for_ERC20(amount_in_wei, arb_bot, token_address, router_instance, recipient_address) ### it needs to be changed to add swap ERC20 -> ERC20
                time.sleep(interval)
    
# def regular_trading_sims(end_time, interval):
#     while time.time() < end_time:
#         swap_WETH_for_ERC20(amount_in_wei, arb_bot, ERC20_instance, router_instance, recipient_address)
#         time.sleep(interval)
 
def setup_sim_account(base_assets, erc20_abi, amount_in_ETH, arb_bot, weth, router, recipient_address):
    """
    Sets up simulation account with 100 ETH worth of value for each baseAsset as specified in the config file.

    Params:
        address (str): The public address of the sim account.
        private_key (str): The private key of the sim account.
    """

    # For every base asset, try to equivalent worth of the asset in address 2.
    for token in base_assets:
        token_address = token["address"]
        token_contract = arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        assert swap_ETH_for_ERC20(amount_in_ETH, arb_bot, weth, token_contract, router, recipient_address) == 1, "Unexpected! Swap WETH-ERC20 failed!"

    print(f'''Balance of the trade simulation address:
    {get_account_balances(arb_bot.web3, recipient_address)}
    ''')

if __name__ == "__main__":
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    
    regular_trader_address = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
    regular_trader_key = '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a'

    arb_bot = ArbBot(500, 100, whale_private_key)
    
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
    uniswap_router = arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
    weth = arb_bot.web3.eth.contract(address=weth_address, abi=weth_abi)

    setup_sim_account(base_assets, erc20_abi, 200, arb_bot, weth, uniswap_router, whale_address) # whale trader holds ~$600k worth of each asset in accout
    setup_sim_account(base_assets, erc20_abi, 5, arb_bot, weth, uniswap_router, regular_trader_address) # regular trader holds ~$15k worth of each asset in account

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    whale_trading_sims(arb_bot, end_time, 60, uniswap_router, base_assets, whale_address) ##!! this needs to be called by the whale address