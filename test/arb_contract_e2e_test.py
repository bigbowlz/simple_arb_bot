import json
import os
from web3 import Web3
from utilities.populate_routes import (
    setup,
    get_token_decimals,
    is_valid_pair,
    check_route,
    )
from utilities.approve_lp import (
    to_wei
)

web3, data, api_key, api_url = setup()
arb_contract_address = "0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94"
arb_contract_abi = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "stateMutability": "payable",
      "type": "fallback"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_router1",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_router2",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_token1",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_token2",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_amount",
          "type": "uint256"
        }
      ],
      "name": "estimateTradeReturn",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_router1",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_router2",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_token1",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_token2",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_amount",
          "type": "uint256"
        }
      ],
      "name": "executeTrade",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_tokenContractAddress",
          "type": "address"
        }
      ],
      "name": "getBalance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "withdrawETH",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_tokenAddress",
          "type": "address"
        }
      ],
      "name": "withdrawToken",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "receive"
    }
]
arb_contract = web3.eth.contract(address=arb_contract_address, abi=arb_contract_abi)
owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
USDT_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDC_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_iCAN_address = "0xa9efDEf197130B945462163a0B852019BA529a66"

print(f'''contract address: {arb_contract_address}
      All functions: {arb_contract.all_functions()}''')

# test estimateTradeReturn(address,address,address,address,uint256)
est_return = arb_contract.functions.estimateTradeReturn(
    _router1 = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    _router2 = "0xEfF92A263d31888d860bD50809A8D171709b7b1c",
    _token1 = "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    _token2 = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    _amount = to_wei(10, 6)).call()
print(f"estimated return is {est_return}")

# test executeTrade(address,address,address,address,uint256)


# test getBalance(address)
assert arb_contract.functions.getBalance(USDC_address).call()==0, "Unexpected! USDC balance is not 0"

# test owner()
assert arb_contract.functions.owner().call({"from": owner_address})==owner_address, "owner() test failed"

# test withdrawETH()

# test withdrawToken(address)