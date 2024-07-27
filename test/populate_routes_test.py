# Before running the test script, please first start a localhost with the command:
# chmod +x scripts/setup.sh && ./scripts/setup.sh

import pytest
import json
import os
from web3 import Web3
from utilities.populate_routes import (
    setup,
    populate_routes,
    check_route,
    is_valid_pair,
    get_token_decimals
    )

web3, data, api_key, api_url = setup()

uniswap_v2_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
sushiswap_v2_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
pancake_v2_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
USDC_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
WBTC_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"

USDC_iCAN_address = 0xa9efDEf197130B945462163a0B852019BA529a66
USDC_iCAN_decimal = 6
BTC_iCAN_address = 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
BTC_iCAN_decimal = 8
SHIB_address = 0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE
SHIB_decimal = 18

# Load router ABI
with open('configs/router_ABIs/UniswapV2Router02_abi.json', 'r') as uniswap_v2_abi_file:
    uniswap_v2_abi = json.load(uniswap_v2_abi_file)
with open('configs/router_ABIs/SushiSwapV2Router02_abi.json', 'r') as sushiswap_v2_abi_file:
    sushiswap_v2_abi = json.load(sushiswap_v2_abi_file)
with open('configs/router_ABIs/PancakeRouter_abi.json', 'r') as pancake_v2_abi_file:
    pancake_v2_abi = json.load(pancake_v2_abi_file)

# Create contract instances for the routers
uniswap_v2 = web3.eth.contract(address=uniswap_v2_address, abi=uniswap_v2_abi)
sushiswap_v2 = web3.eth.contract(address=sushiswap_v2_address, abi=sushiswap_v2_abi)
pancake_v2 = web3.eth.contract(address=pancake_v2_address, abi=pancake_v2_abi)

def test_get_token_decimals():
    assert USDC_iCAN_decimal == get_token_decimals(USDC_iCAN_address, web3)
    assert BTC_iCAN_decimal == get_token_decimals(BTC_iCAN_address, web3)
    assert SHIB_decimal == get_token_decimals(SHIB_address, web3)

def test_is_valid_pair():
    #assert is_valid_pair(uniswap_v2, USDC_address, WBTC_address)
    assert is_valid_pair(sushiswap_v2, WBTC_address, USDC_address)
    #assert is_valid_pair(pancake_v2, USDC_address, WBTC_address)

'''def test_check_route():
'''

"""@patch('populate_routes.check_route', return_value=True)
def test_populate_routes(mock_check_route):
    data = {
        "routers": [
            {"dex": "uniswap", "address": "0x123"},
            {"dex": "sushiswap", "address": "0x456"}
        ],
        "tokens": [
            {"address": "0xAAA"},
            {"address": "0xBBB"}
        ],
        "routes": []
    }
    web3 = MagicMock()

    populate_routes(data, web3)

    assert len(data["routes"]) == 1
    assert data["routes"][0] == {
        "router1": "0x123",
        "router2": "0x456",
        "token1": "0xAAA",
        "token2": "0xBBB"
    }
"""




if __name__ == "__main__":
    pytest.main()
