from utilities.arb_bot import ArbBot
from sims import (setup_sim_account, trading_sims)
import json
"""
Simulates whale trader activities on UniswapV2. 
The whale account holds ~$1.8m worth of each baseAsset in the config file.
Every 10 seconds, the whale trades a random baseAsset for another random baseAsset 
for a random value between $10,000 and $1,000,000 in a single swap.

Author: ILnaw
Version: 08-14-2024
"""

if __name__ == "__main__":
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(500, 100, whale_private_key)
    
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

    # whale trader holds ~$1.8m worth of each asset in account
    print("Setting up whale account...")
    print(f'''
    Whale account balances:
    {setup_sim_account(base_assets, erc20_abi, 600, whale_arb_bot, weth, uniswap_router, whale_address)}
    ''') 

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    # Transaction sent by the whale address through whale_arb_bot setup, trading between $5,000 and $100,000 in a single swap.
    trading_sims(whale_arb_bot, 10_000, 1_000_000, end_time, 10, uniswap_router, base_assets, whale_address)