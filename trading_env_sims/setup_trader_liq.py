from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (get_account_balances)
from trading_env_sims.sim_utilities import (setup_sim_account)
from utilities.approve_lp import (fund_pool)
import json
"""
Set up regular trader account and whale trader account with liquidity, and use 
whale account to fund all routers with base asset pools.

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

                print(f'amount_token1 to fund: {amount_token1}')
                print(f'amount_token2 to fund: {amount_token2}')

                # create pair for each baseAsset pair and fund router with balances 
                try:
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
                except:
                    print("Fund pool failed.")
                print("---------------------------")
    return get_account_balances(arb_bot.web3, arb_bot.sender_address) 
if __name__ == "__main__":
    regular_trader_address = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC' # the regular trader simulator address
    regular_trader_key = '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a'
    regular_trader_arb_bot = ArbBot(regular_trader_key)

    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(whale_private_key)
    
    regular_trader_erc20_address = '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65' # the regular trader erc20 simulator address
    regular_trader_erc20_key = '0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a'
    regular_trader_erc20_arb_bot = ArbBot(regular_trader_erc20_key)

    whale_erc20_address = '0x90F79bf6EB2c4f870365E785982E1f101E93b906' # the whale erc20 simulator address
    whale_erc20_private_key = '0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6' # private key of the whale_erc20 simulator address
    whale_erc20_arb_bot = ArbBot(whale_erc20_private_key)

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
    uniswap_router = regular_trader_arb_bot.web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = regular_trader_arb_bot.web3.eth.contract(address=sushi_router_address, abi=uniswap_router_abi)

    pancake_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    pancake_router = regular_trader_arb_bot.web3.eth.contract(address=pancake_router_address, abi=uniswap_router_abi)
    
    # regular trader holds ~$15k ETH worth of each asset traded from sushi_router in account
    print("Setting up regular trader account...")
    print(f'''
Regular trader account balances:
{setup_sim_account(base_assets, erc20_abi, 5, regular_trader_arb_bot, sushi_router, regular_trader_address)}
''') 
    
    # regular erc20 trader holds ~$15k ETH worth of each asset traded from uniswap_router in account
    print("Setting up regular erc20 trader account...")
    print(f'''
Regular erc20 trader account balances:
{setup_sim_account(base_assets, erc20_abi, 5, regular_trader_erc20_arb_bot, uniswap_router, regular_trader_erc20_address)}
''') 

    # whale trader holds ~$300k ETH worth of each asset traded from sushi_router in account
    print(f"Setting up whale account...")
    print(f'''
Whale account balances:
{setup_sim_account(base_assets, erc20_abi, 100, whale_arb_bot, sushi_router, whale_address)}
''') 
    
    # whale erc20 trader holds ~$300k ETH worth of each asset traded from uniswap_router in account
    print(f"Setting up whale erc20 account...")
    print(f'''
Whale account balances:
{setup_sim_account(base_assets, erc20_abi, 100, whale_erc20_arb_bot, uniswap_router, whale_erc20_address)}
''') 

    print(f'LPing all routers with liquidity for all base asset pairs...')
    print(f'''
Whale account balances after LP: 
{LP_base_pairs_for_all_routers(data["routers"], data["baseAssets"], whale_arb_bot)}''')