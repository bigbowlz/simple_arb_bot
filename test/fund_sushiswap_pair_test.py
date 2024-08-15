from utilities.approve_lp import (fund_pool)
from utilities.arb_bot import ArbBot
from utilities.trading_utilities import (approve_tokens, get_account_balances)
import json

whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
whale_arb_bot = ArbBot(whale_private_key)

# create SushiRouter instance
with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as file:
    uniswap_router_abi = json.load(file)
router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
router = whale_arb_bot.web3.eth.contract(address=router_address, abi=uniswap_router_abi)

# create Sushi Factory instance
with open("configs/factory_ABIs/UniswapV2Factory_abi.json", "r") as factory_abi_file:
    factory_abi = json.load(factory_abi_file)
factory_address = router.functions.factory().call()
factory = whale_arb_bot.web3.eth.contract(address=factory_address, abi=factory_abi)

with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
    erc20_abi = json.load(erc20_abi_file)
USDT_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDT_instance = whale_arb_bot.web3.eth.contract(address=USDT_address, abi=erc20_abi)
SHIB_address = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
SHIB_instance = whale_arb_bot.web3.eth.contract(address=SHIB_address, abi=erc20_abi)

# print(fund_pool(whale_arb_bot.web3, factory, router, USDT_instance, SHIB_instance, 36578658748, 1709395281363466048241664, whale_private_key))

print(f"USDT balance: {get_account_balances(whale_arb_bot.web3, whale_address)["SHIB"]}")
print(approve_tokens(whale_arb_bot.web3, SHIB_instance, router_address, 1709395281363466048241664, whale_private_key))