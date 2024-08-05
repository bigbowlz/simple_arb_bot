from web3 import Web3
from utilities.populate_routes import (
    setup,
    get_token_decimals
    )
import time
import json
from utilities.balances import (to_wei, sign_and_send_tx)

'''
approve_lp.py

Create pairs for two tokens and add liquidity for them on router.

Author: ILnaw
Version: 08-05-2024
'''

def approve_tokens(web3, token_contract, spender_address, amount, private_key):
    """
    Approves spender_address to spend an amount of token from signer.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        token_contract (Contract): Contract instance of the token.
        spender_address (str): address of the spender. 
        amount (int): amount of token to approve.
        private_key (str): private key of the signer.

    Returns:
        receipt (receipt): receipt of the approval transaction.
    """
    tx = token_contract.functions.approve(spender_address, amount).build_transaction({
        'from': web3.eth.accounts[0],
        'nonce': web3.eth.get_transaction_count(web3.eth.accounts[0]),
        'gas': 200000,
        'maxFeePerGas': web3.to_wei('20', 'gwei')
    })
    
    receipt = sign_and_send_tx(web3, tx, private_key)
    print(f"Approved {amount} of token {token_contract.address} to spender {spender_address}")
    return receipt

def create_pair(web3, factory_contract, tokenA, tokenB, private_key):
    """
    Creates a token pair tokenA - tokenB on the factory contract of a dex.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        factory_contract (Contract): Factory contract instance of a dex.
        tokenA (Contract): contract instance of tokenA.
        tokenB (Contract): contract instance of tokenB.
        private_key (str): private key of the signer.

    Returns:
        receipt (receipt): receipt of the pair creation transaction.
    """
    tx = factory_contract.functions.createPair(tokenA, tokenB).build_transaction({
        'from': web3.eth.accounts[0],
        'nonce': web3.eth.get_transaction_count(web3.eth.accounts[0]),
        'gas': 3000000,
        'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei')
    })
    
    receipt = sign_and_send_tx(web3, tx, private_key)
    print(f"Pair created: {tokenA} - {tokenB}")
    return receipt

def add_liquidity(web3, router_contract, tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin, private_key):
    """
    Add liquidity to the pool tokenA - tokenB on the router contract of a dex for a specified amount.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        router_contract (Contract): Router contract instance of a dex.
        tokenA (Contract): contract instance of tokenA.
        tokenB (Contract): contract instance of tokenB.
        amountADesired (int): amount to add for tokenA.
        amountBDesired (int): amount to add for tokenB.
        amountAMin (int): minimum amount accepted for the LP result for tokenA.
        amountBMin (int): minimum amount accepted for the LP result for tokenB.
        private_key (str): private key of the signer.

    Returns:
        receipt (receipt): receipt of the pair creation transaction.
    """
    deadline = int(time.time()) + 60 * 20  # 20 minutes from now

    tx = router_contract.functions.addLiquidity(
        tokenA.address, tokenB.address, amountADesired, amountBDesired, amountAMin, amountBMin, web3.eth.accounts[0], deadline
    ).build_transaction({
        'from': web3.eth.accounts[0],
        'nonce': web3.eth.get_transaction_count(web3.eth.accounts[0]),
        'gas': 1000000,
        'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei')
    })
    
    assert router_contract.functions.factory().call() == "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    receipt = sign_and_send_tx(web3, tx, private_key)
    assert router_contract.functions.WETH().call() == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    print(f"Liquidity added successfully to router {router_contract.address}")
    return receipt

def fund_pool(web3, factory, router, token1, token2, amount_token1, amount_token2, private_key):
    """
    Add liquidity to the pool tokenA - tokenB on the router contract of a dex for a specified amount.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        factory
        router (Contract): Router contract instance of a dex.
        token1 (Contract): contract instance of token1.
        token2 (Contract): contract instance of token2.
        amount_token1 (int): amount to add for token1.
        amount_token2 (int): amount to add for token2.
        private_key (str): private key of the signer.

    Returns:
        bool or receipt (receipt): False if any step fails, or receipt of the pair creation transaction.
    """
    # Check if the pair exists
    pair_address = factory.functions.getPair(token1.address, token2.address).call()
    if pair_address == '0x0000000000000000000000000000000000000000':
        try:
            create_pair(web3, factory, token1.address, token2.address, private_key)
        except Exception as e:
            print(f"Error while trying to create pair: {e}")
            return False

    # Approve tokens
    amount_token1_approve = to_wei(200, get_token_decimals(token1.address, web3)) 
    amount_token2_approve = to_wei(10000000, get_token_decimals(token2.address, web3)) 

    try:
        approve_tokens(web3, token1, router.address, amount_token1_approve, private_key)
        approve_tokens(web3, token2, router.address, amount_token2_approve, private_key)
    except Exception as e:
        print(f"Error while trying to approve tokens: {e}")
        return False
    try:
        return add_liquidity(
            web3,
            router, 
            token1, 
            token2, 
            amount_token1, 
            amount_token2, 
            int(amount_token1*0.8), 
            int(amount_token2*0.8),
            private_key)
    except Exception as e:
        print(f"Error while trying to create pool: {e}")
        return False

if __name__ == "__main__":
    
    # Connect to your Ethereum node (Infura, local node, etc.)
    web3, data, api_key, api_url = setup()

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
        factory_abi = json.load(factory_abi_file)
        print("factory_abi read from json file.")

    with open("configs/router_ABIs/UniswapV2Router02_abi.json", "r") as router_abi_file:
        router_abi = json.load(router_abi_file)
        print("router_abi read from json file.")
        
    # Addresses
    owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    uniswap_factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    uniswap_factory = web3.eth.contract(address=uniswap_factory_address, abi=factory_abi)
    uniswap_router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    uniswap_router_contract = web3.eth.contract(address=uniswap_router_address, abi=router_abi)

    btc_iCAN_address = '0x49AeF2C4005Bf572665b09014A563B5b9E46Df21'
    btc_iCAN_contract = web3.eth.contract(address=btc_iCAN_address, abi=token_abi)

    usdc_iCAN_address = '0xa9efDEf197130B945462163a0B852019BA529a66'
    usdc_iCAN_contract = web3.eth.contract(address=usdc_iCAN_address, abi=token_abi)

    amount_btc_lp = to_wei(100, 8)
    amount_usdc_lp = to_wei(5000000, 6)

    fund_pool(web3, uniswap_factory, uniswap_router_contract, btc_iCAN_contract, usdc_iCAN_contract, amount_btc_lp, amount_usdc_lp, private_key)
