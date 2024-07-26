import pytest
from web3 import Web3
from utilities.populate_routes import (
    setup,
    populate_routes,
    is_valid_pair,
    get_token_decimals
    )

web3, data, api_key, api_url = setup()

def test_get_token_decimals():
    USDC_iCAN_address = 0xa9efDEf197130B945462163a0B852019BA529a66
    USDC_iCAN_decimal = 6
    BTC_iCAN_address = 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
    BTC_iCAN_decimal = 8
    SHIB_address = 0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE
    SHIB_decimal = 18

    assert USDC_iCAN_decimal == get_token_decimals(USDC_iCAN_address, web3)
    assert BTC_iCAN_decimal == get_token_decimals(BTC_iCAN_address, web3)
    assert SHIB_decimal == get_token_decimals(SHIB_address, web3)


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

@patch('populate_routes.get_token_decimals', return_value=18)
@patch('populate_routes.Web3')
def test_is_valid_pair(MockWeb3, mock_get_token_decimals):
    mock_router = MagicMock()
    mock_router.functions.getAmountsOut.return_value.call.return_value = [1, 2]

    assert is_valid_pair(mock_router, "0xAAA", "0xBBB")
"""

if __name__ == "__main__":
    pytest.main()
