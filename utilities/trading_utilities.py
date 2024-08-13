from decimal import Decimal
from web3 import Web3
import os
import json
'''
trading_utilities.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 08-04-2024
'''

def to_wei(amount, decimals):
    """
    Converts amount in eth units to in wei units.

    Params:
        amount (int): Amount in eth.
        decimals (int): The decimals for the conversion. 

    Returns:
        int: amount * 10 ** decimals
    """
    return int(Decimal(amount) * 10**decimals)

def from_wei(amount_in_wei, decimals):
    """
    Converts amount in wei units to in eth units.

    Params:
        amount_in_wei (int): Amount in wei.
        decimals (int): The decimals for the conversion. 

    Returns:
        int: amount / 10 ** decimals
    """
    return int(Decimal(amount_in_wei) / (10**decimals))

def sign_and_send_tx(web3, tx, private_key):
    """
    Sign and send a transaction.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
        tx (dict): A dictionary conforming to the web3.eth.send_transaction(transaction) method.
        private_key (str): Hex value of a private key.

    Returns:
        tx_receipt (receipt): the receipt of a transaction.
    """
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt

def get_token_decimals(token_address, web3):
    '''
    Get the number of decimals for a token.

    Params:
        token_address: the string address of the token contract.
        web3: an instance of the Web3 class from the web3.py library.

    Returns:
        int: the decimal of a token.
    '''
    erc20_abi = '[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]'

    token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)
    return token_contract.functions.decimals().call()

def get_account_balances(web3, address):
    '''
    Get the balance of all tokens in an account based on the baseAssets specified in the mainnet config file.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
        address (str): address to check for balances.

    Returns:
        balances (dict): balances of all tokens in a dictionary.
    '''
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
    ETH_balance = web3.eth.get_balance(address)
    balances = {"ETH": ETH_balance}
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

    for token in data["baseAssets"]:
        token_address = token["address"]
        token_sym = token["sym"]
        token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)
        token_balance = token_contract.functions.balanceOf(address).call()
        balances[token_sym] =token_balance
    return balances

def approve_tokens(web3, token_contract, spender_address, amount, private_key):
    """
    Approves spender_address to spend an amount of token from signer.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
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

def get_estimated_return(web3, router_instance, amount_in, token_in, token_out):
    """
    Gets the estimated trade return when trading in a specified amount of a token for another on a router.

    Params:
        web3 (Provider): a Provider instance to access blockchain. Takes JSON-RPC requests and returns the response.
        router_instance (Contract): a contract instance for the router.
        amount_in (int): the amount in wei to be traded in.
        token_in (str): the address of the token to be traded in.
        token_out (str): the address of the trade return token.

    Returns:
        amounts_out (int): the value of the return token in wei.
    """
    # Convert the amount to the correct units (e.g., from ETH to wei)
    amount_in_wei = web3.to_wei(amount_in, 'ether')
    
    # Call the `getAmountsOut` function
    amounts_out = router_instance.functions.getAmountsOut(
        amount_in_wei,
        [token_in, token_out]
    ).call()
    
    return amounts_out # returns the amount in wei

def wrap_ETH_to_WETH(amount_in_wei, arb_bot, weth_instance):
    """
    Wraps ETH to WETH in sender_address.

    Params:
        amount_in_wei (int): amount in wei to swap in.
        arb_bot (ArbBot): an ArbBot contract instance with the sender address as the owner.
        weth_instance (Contract): a contract instance for WETH.

    Returns:
        wrap_tx_receipt (dict): receipt of the wrapping transaction.
    """
    wrap_tx = weth_instance.functions.deposit().build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'value': amount_in_wei  # Amount of ETH to wrap into WETH
    })

    wrap_tx_receipt = sign_and_send_tx(arb_bot.web3, wrap_tx, arb_bot.private_key)

    return wrap_tx_receipt

def swap_ERC20_for_ERC20(amount_in_wei, arb_bot, ERC20_address_1, ERC20_address_2, router_instance, recipient_address):
    """
    Swaps WETH in sender_address to ERC20 on router, and sends the ERC20 to a recipient address.

    Params:
        amount_in_wei (int): amount in wei to swap in.
        arb_bot (ArbBot): an ArbBot contract instance with the sender address as the owner.
        ERC20_address_1 (str): address of the token being swapped in.
        ERC20_address_2 (str): address of the token being swapped out.
        router_instance (Contract): a contract instance for the router.
        recipient_address (str): the address of the recipient. 

    Returns:
        swap_receipt (dict): the receipt of the swapping transaction.
    """
    path = [ERC20_address_1, ERC20_address_2]
    amount_out_min = int(amount_in_wei / 10 ** 12)
    deadline = int(arb_bot.web3.eth.get_block('latest')['timestamp']) + 300  # 5 minutes from the current block time

    swap_tx = router_instance.functions.swapExactTokensForTokens(
        amount_in_wei,
        amount_out_min,
        path,
        recipient_address,
        deadline
    ).build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
    })

    swap_receipt = sign_and_send_tx(arb_bot.web3, swap_tx, arb_bot.private_key)

    return swap_receipt

def approve_ERC20_on_Router(amount_in_wei, arb_bot, ERC20_instance, router_instance):
    """
    Approves ERC20 spending on a router.

    Params:
        amount_in_wei (int): amount in wei to swap in.
        arb_bot (ArbBot): an ArbBot contract instance.
        ERC20_instance (Contract): a contract instance for the ERC20 token.
        router_instance (Contract): a contract instance for the router.

    Returns:
        ERC20_approval_receipt (dict): the receipt of the WETH approval transaction.
    """
    approve_tx = ERC20_instance.functions.approve(router_instance.address, amount_in_wei).build_transaction({
        'chainId': arb_bot.chain_id,
        'gas': 400000,
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
    })
    ERC20_approval_receipt = sign_and_send_tx(arb_bot.web3, approve_tx, arb_bot.private_key)

    allowance = ERC20_instance.functions.allowance(arb_bot.sender_address, router_instance.address).call()
    decimal = ERC20_instance.functions.decimals().call()
    symbol = ERC20_instance.functions.symbol().call()

    if ERC20_approval_receipt['status'] == 1:
      print(f"Current {symbol} allowance on router: {from_wei(allowance, decimal)} {symbol}")
    else:
      print(f'{symbol} approval failed.')

    return ERC20_approval_receipt
