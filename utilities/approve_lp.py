from web3 import Web3
from utilities.populate_routes import (
    setup
    )
import time
import json
from utilities.balances import (to_wei)

# Connect to your Ethereum node (Infura, local node, etc.)
web3, data, api_key, api_url = setup()

# Your Ethereum account
owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'

# Token and Router addresses
uniswap_factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
uniswap_router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
btc_iCAN_address = '0x49AeF2C4005Bf572665b09014A563B5b9E46Df21'
usdc_iCAN_address = '0xa9efDEf197130B945462163a0B852019BA529a66'

# ABI definitions
token_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

with open("configs/factory_ABIs/UniswapV2Factory_abi.json", "r") as factory_abi_file:
    uniswap_factory_abi = json.load(factory_abi_file)
    print("factory_abi read from json file.")

with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as router_abi_file:
    router_abi = json.load(router_abi_file)
    print("router_abi read from json file.")

def send_transaction(tx):
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def approve_tokens(token_address, spender_address, amount):
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    tx = token_contract.functions.approve(spender_address, amount).build_transaction({
        'from': owner_address,
        'nonce': web3.eth.get_transaction_count(owner_address),
        'gas': 200000,
        'maxFeePerGas': web3.to_wei('20', 'gwei')
    })
    
    receipt = send_transaction(tx)
    print(f"Approved {amount} of token {token_address} to spender {spender_address}")
    return receipt

def create_pair(factory_contract, tokenA, tokenB):
    tx = factory_contract.functions.createPair(tokenA, tokenB).build_transaction({
        'from': owner_address,
        'nonce': web3.eth.get_transaction_count(owner_address),
        'gas': 3000000,
        'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei')
    })
    
    receipt = send_transaction(tx)
    print(f"Pair created: {tokenA} - {tokenB}")
    return receipt


def add_liquidity(router_address, tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin):
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)
    deadline = int(time.time()) + 60 * 20  # 20 minutes from now

    tx = router_contract.functions.addLiquidity(
        tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin, owner_address, deadline
    ).build_transaction({
        'from': owner_address,
        'nonce': web3.eth.get_transaction_count(owner_address),
        'gas': 1000000,
        'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei')
    })
    
    assert router_contract.functions.factory().call() == "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    receipt = send_transaction(tx)
    assert router_contract.functions.WETH().call() == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    print(f"Liquidity added successfully to router {router_address}")
    return receipt

def main():
    # Check if the pair exists
    uniswap_factory = web3.eth.contract(address=uniswap_factory_address, abi=uniswap_factory_abi)
    pair_address = uniswap_factory.functions.getPair(btc_iCAN_address, usdc_iCAN_address).call()
    if pair_address == '0x0000000000000000000000000000000000000000':
        try:
            create_pair(uniswap_factory, btc_iCAN_address, usdc_iCAN_address)
        except Exception as e:
            print(f"Error while trying to create pair: {e}")
            return

    # Approve tokens
    amount_btc_approve = to_wei(200, 8)  # BTC has 8 decimals
    amount_usdc_approve = to_wei(10000000, 6)  # USDC has 6 decimals

    try:
        approve_tokens(btc_iCAN_address, uniswap_router_address, amount_btc_approve)
        approve_tokens(usdc_iCAN_address, uniswap_router_address, amount_usdc_approve)
    except Exception as e:
        print(f"Error while trying to approve tokens: {e}")

    amount_btc_lp = to_wei(100, 8)
    amount_btc_lp_min = to_wei(90, 8)
    amount_usdc_lp = to_wei(5000000, 6)
    amount_usdc_lp_min = to_wei(4000000, 6)

    try:
        add_liquidity(
            uniswap_router_address, 
            btc_iCAN_address, 
            usdc_iCAN_address, 
            amount_btc_lp, 
            amount_usdc_lp, 
            amount_btc_lp_min, 
            amount_usdc_lp_min)
    except Exception as e:
        print(f"Error while trying to create pool: {e}")

if __name__ == "__main__":
    main()
