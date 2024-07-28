# Before running the test script, please first start a localhost with the command:
# chmod +x scripts/setup.sh && ./scripts/setup.sh

import pytest
import json
import os
from web3 import Web3
from utilities.populate_routes import (
    setup,
    get_token_decimals,
    is_valid_pair,
    populate_routes,
    check_route
    )

web3, data, api_key, api_url = setup()

uniswap_v2_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
sushiswap_v2_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
pancake_v2_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"

USDC_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_decimal = 6

WBTC_address = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
WBTC_decimal = 8

MATIC_address = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"
MATIC_decimal = 18

LINK_address = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
LINK_decimal = 18

SHIB_address = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
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
    assert MATIC_decimal == get_token_decimals(MATIC_address, web3)
    assert LINK_decimal == get_token_decimals(LINK_address, web3)
    assert SHIB_decimal == get_token_decimals(SHIB_address, web3)
    assert USDC_decimal == get_token_decimals(USDC_address, web3)
    assert WBTC_decimal == get_token_decimals(WBTC_address, web3)


def test_is_valid_pair():
    assert is_valid_pair(uniswap_v2, WBTC_address, USDC_address, web3)
    assert is_valid_pair(pancake_v2, USDC_address, WBTC_address, web3)
    assert not is_valid_pair(sushiswap_v2, USDC_address, WBTC_address, web3)

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
