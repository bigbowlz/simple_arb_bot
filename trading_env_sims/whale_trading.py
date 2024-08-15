from utilities.arb_bot import ArbBot
from sims import (setup_sim_account, trading_sims)
from utilities.approve_lp import (fund_pool)
from utilities.trading_utilities import (get_account_balances, get_estimated_return)
import json
"""
Simulates whale trader activities on UniswapV2. 
The whale account holds ~$300k worth of each baseAsset in the config file.
Every 10 seconds, the whale trades a random baseAsset for another random baseAsset 
for a random value between $20,000 and $50,000 in a single swap.

Author: ILnaw
Version: 08-14-2024
"""
def LP_base_pairs_for_all_routers(routers, base_assets, arb_bot):
    """
        Provide liquidity for all baseAsset pairs on all routers in the config file using 10% of the balance on account.

        Params:
            routers (list): a list of routers. Each router is a dict of a "dex" key and an "address" key.
            base_assets (list): a list of base assets for trading. Each asset is a dict of a "sym" key and an "address" key.
            arb_bot (ArbBot): an ArbBot instance. 

        Returns:
            balances (dict): balances of all tokens in a dictionary.
    """
    # load abi file data for contract instantiation for factory, router and token contracts
    with open("configs/factory_ABIs/UniswapV2Factory_abi.json", "r") as factory_abi_file:
        factory_abi = json.load(factory_abi_file)
    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as router_abi_file:
        router_abi = json.load(router_abi_file)
    with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
        erc20_abi = json.load(erc20_abi_file)

    # loop through each router and add liquidity for each base asset pair
    for router in routers:
        router_address = router["address"]
        router_contract = arb_bot.web3.eth.contract(address=router_address, abi=router_abi)
        factory_address = router_contract.functions.factory().call()
        factory_contract = arb_bot.web3.eth.contract(address=factory_address, abi=factory_abi)
        print("")
        print(f'LPing for {router["dex"]}')

        for i in range(len(base_assets)-1):
            for j in range(i+1, len(base_assets)):
                token1_address = base_assets[i]["address"]
                token2_address = base_assets[j]["address"]
                token1_contract = arb_bot.web3.eth.contract(address=token1_address, abi=erc20_abi)
                token2_contract = arb_bot.web3.eth.contract(address=token2_address, abi=erc20_abi)
                token1_balance = token1_contract.functions.balanceOf(arb_bot.sender_address).call()
                token2_balance = token2_contract.functions.balanceOf(arb_bot.sender_address).call()
                amount_token1 = int(token1_balance/10)
                amount_token2 = int(token2_balance/10)
                # try:
                #     amount_token2 = get_estimated_return(
                #         arb_bot.web3,
                #         router_contract,
                #         amount_token1,
                #         token1_address,
                #         token2_address)
                # except:
                #     print(f'Estimating return failed from {token1_contract.functions.symbol().call()} to {token2_contract.functions.symbol().call()}.')
                print(f'amount_token1 to fund: {amount_token1}')
                print(f'amount_token2 to fund: {amount_token2}')

                # create pair for each baseAsset pair and fund router with balances 
                fund_pool(
                    arb_bot.web3, 
                    factory_contract, 
                    router_contract, 
                    token1_contract, 
                    token2_contract, 
                    amount_token1, 
                    amount_token2,
                    arb_bot.private_key
                )
                print("---------------------------")
    return get_account_balances(arb_bot.web3, arb_bot.sender_address) 

if __name__ == "__main__":
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(whale_private_key)
    
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

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = whale_arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
    weth = whale_arb_bot.web3.eth.contract(address=weth_address, abi=weth_abi)

    # whale trader holds ~$600k ETH worth of each asset traded from SushiSwap in account
    print(f'''Setting up whale account...
Whale account balances:
{setup_sim_account(base_assets, erc20_abi, 200, whale_arb_bot, weth, sushi_router, whale_address)}
''') 

    print(f'''LPing all routers with liquidity for all base asset pairs...
Whale account balances after LP: 
{LP_base_pairs_for_all_routers(data["routers"], data["baseAssets"], whale_arb_bot)}''')

    # Loads ArbBot configs to get end_time of the simulation.
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    end_time = start_time + duration

    # Transaction sent by the whale address through whale_arb_bot setup, trading between $50,000 and $100,000 in a single swap.
    trading_sims(whale_arb_bot, 10_000, 50_000, end_time, 5, uniswap_router, base_assets, whale_address)