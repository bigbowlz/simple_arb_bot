from web3 import Web3
from utilities.populate_routes import (
    setup,
    get_token_decimals,
    is_valid_pair,
    check_route,
    )
import time
from decimal import Decimal

# Connect to your Ethereum node (Infura, local node, etc.)
web3, data, api_key, api_url = setup()

# Your Ethereum account
owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'

# Token and Router addresses
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

router_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "amountADesired", "type": "uint256"},
            {"name": "amountBDesired", "type": "uint256"},
            {"name": "amountAMin", "type": "uint256"},
            {"name": "amountBMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amountA", "type": "uint256"},
            {"name": "amountB", "type": "uint256"},
            {"name": "liquidity", "type": "uint256"}
        ],
        "type": "function"
    }
]

def send_transaction(tx):
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def approve_tokens(token_address, spender_address, amount):
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    tx = token_contract.functions.approve(spender_address, amount).buildTransaction({
        'from': owner_address,
        'nonce': web3.eth.getTransactionCount(owner_address),
        'gas': 200000,
        'gasPrice': web3.toWei('20', 'gwei')
    })
    
    receipt = send_transaction(tx)
    print(f"Approved {amount} of token {token_address} to spender {spender_address}")
    return receipt

def create_pool(router_address, tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin):
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)
    deadline = int(time.time()) + 60 * 20  # 20 minutes from now
    
    tx = router_contract.functions.addLiquidity(
        tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin, owner_address, deadline
    ).buildTransaction({
        'from': owner_address,
        'nonce': web3.eth.getTransactionCount(owner_address),
        'gas': 400000,
        'gasPrice': web3.toWei('20', 'gwei')
    })
    
    receipt = send_transaction(tx)
    print(f"Liquidity added successfully to router {router_address}")
    return receipt

def to_wei(amount, decimals):
    return int(Decimal(amount) * 10**decimals)

def main():
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
        create_pool(uniswap_router_address, btc_iCAN_address, usdc_iCAN_address, amount_btc_lp, amount_usdc_lp, amount_btc_lp_min, amount_usdc_lp_min)
    except Exception as e:
        print(f"Error while trying to create pool: {e}")

if __name__ == "__main__":
    main()
