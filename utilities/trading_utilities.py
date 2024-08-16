from decimal import Decimal
from web3 import Web3
import json
'''
trading_utilities.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 08-14-2024
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
        amount (int): amount of token to approve in wei.
        private_key (str): private key of the signer.

    Returns:
        receipt (receipt): receipt of the approval transaction.
    """
    signer_wallet = web3.eth.account.from_key(private_key)
    owner_address = signer_wallet.address
    tx = token_contract.functions.approve(spender_address, amount).build_transaction({
        'from': owner_address,
        'nonce': web3.eth.get_transaction_count(owner_address),
        'gas': 800000,
        'maxFeePerGas': web3.to_wei('20', 'gwei')
    })
    
    receipt = sign_and_send_tx(web3, tx, private_key)
    token_amount_in_ETH = from_wei(amount, get_token_decimals(token_contract.address, web3))
    token_symbol = token_contract.functions.symbol().call()
    print(f"Approved {token_amount_in_ETH} {token_symbol} from {owner_address} to {spender_address}")
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
    amounts_out = "N/A"
    # Call the `getAmountsOut` function
    try: 
        amounts_out = router_instance.functions.getAmountsOut(
            amount_in_wei,
            [token_in, token_out]
        ).call()[-1]
    except:
        print(f"The router getAmountsOut function failed for {token_in} to {token_out}")
    return amounts_out # returns the amount in wei

def wrap_ETH_to_WETH(amount_in_wei, arb_bot):
    """
    Wraps ETH to WETH in sender_address.

    Params:
        amount_in_wei (int): amount in wei to swap in.
        arb_bot (ArbBot): an ArbBot contract instance with the sender address as the owner.

    Returns:
        wrap_tx_receipt (dict): receipt of the wrapping transaction.
    """
    with open("configs/token_ABIs/erc20_abi.json", "r") as erc20_abi_file:
        erc20_abi = json.load(erc20_abi_file)
    weth_instance = arb_bot.web3.eth.contract(address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", abi=erc20_abi)

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
    Swaps ERC20 in sender_address to ERC20 on router, and sends the returned ERC20 to a recipient address.

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
    amount_out_min = 0
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

def get_ERC20_allowance(ERC20_instance, owner_address, router_address):
    return ERC20_instance.functions.allowance(owner_address, router_address).call()

def send_ETH_to_Arb(arb_bot, amount):
    """
    Sends native ETH from sender account to the arb bot contract. 

    Params:
        arb_bot (ArbBot): an ArbBot contract instance.
        amount (int): Amount in wei.

    Returns:
        tx_receipt (receipt): The receipt of the ETH transfer transaction.
    """
    print('Sending ETH from sender_address to arb contract...')
    # Send ETH to Contract
    tx = {
        'from': arb_bot.sender_address,
        'to': arb_bot.bot_address,
        'value': to_wei(amount, 18), 
        'gas': 400000, 
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'chainId': arb_bot.chain_id
    }

    # Sign and send the transaction
    return sign_and_send_tx(arb_bot.web3, tx, arb_bot.private_key)

def swap_ETH_for_ERC20(amount_in_ETH, arb_bot, ERC20_instance, router_instance, recipient_address):
    """
    Swaps 1 native ETH to an ERC20 on a router by wrapping ETH->WETH, approving WETH, 
    swapping WETH for ERC20, and sends the returned ERC20 to the recipient address. 

    Params:
        amount_in_ETH (int): amount in ETH to swap in.
        arb_bot (ArbBot): an ArbBot contract instance.
        ERC20_instance (Contract): a contract instance for ERC20.
        router_instance (Contract): a contract instance for the router.
        recipient_address (str): the address of the recipient. 

    Returns:
        bool: True for a successful execution of the swap; False otherwise.
    """
    # avoid swapping ETH for WETH as it conflicts with path[0] on Uniswapv2 swapExactETHForTokens
    if ERC20_instance.address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2":
        print("Can't swap ETH for WETH. Skipping.")
        return {'status': 0}
    amount_in_wei = to_wei(amount_in_ETH, 18)
    deadline = arb_bot.web3.eth.get_block('latest')['timestamp'] + 60 * 20 # 20 minutes from the current block
    path = [router_instance.functions.WETH().call(), ERC20_instance.address]

    # Prepare the transaction
    tx = router_instance.functions.swapExactETHForTokens(
        0,
        path,
        recipient_address,
        deadline
    ).build_transaction({
        'value': amount_in_wei,
        'gas': 300000,  # Estimate this value correctly
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('20', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
    })
    swap_receipt = sign_and_send_tx(arb_bot.web3, tx, arb_bot.private_key)
    print('''
    ****************************
    *       Swap success!      *
    ****************************
          ''')
    # Print the return token balance on recipient.
    ERC20_balance_on_recipient = ERC20_instance.functions.balanceOf(recipient_address).call()
    token_symbol = ERC20_instance.functions.symbol().call()
    balance_from_wei = from_wei(ERC20_balance_on_recipient, get_token_decimals(ERC20_instance.address, arb_bot.web3))
    print(f"Current {token_symbol} balance on recipient address (int): {balance_from_wei} {token_symbol}")

    return swap_receipt['status']

def send_ERC20(arb_bot, recipient_address, ERC20_contract, amount):
    """
    Sends ERC20 from private_key account to an address. 

    Params:
        sender_private_key (str): private key of the sender account.
        recipient_address (str): address of the recipient.
        ERC20_contract (Contract): contract instance of the ERC20 token.
        amount (int): amount of ERC20 token to send in wei.

    Returns:
        tx_receipt (receipt): The receipt of the ERC20 transfer transaction.
    """
    print(f'Sending {ERC20_contract.functions.symbol().call()} from sender_address to {recipient_address}...')
    # Send ETH to Contract
    tx = ERC20_contract.functions.transfer(
        recipient_address,
        amount
    ).build_transaction({
        'gas': 200000, 
        'maxFeePerGas': arb_bot.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
        'maxPriorityFeePerGas': arb_bot.web3.to_wei('2', 'gwei'),
        'nonce': arb_bot.get_sender_nonce(),
        'chainId': arb_bot.chain_id
    })

    # Sign and send the transaction
    return sign_and_send_tx(arb_bot.web3, tx, arb_bot.private_key)
# the following are for testing purposes and prints all UniswapV2Router's allowances for tokens owned by the whale address
if __name__ == "__main__":
    from utilities.arb_bot import ArbBot
    whale_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' # the whale simulator address
    whale_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d' # private key of the whale simulator address
    whale_arb_bot = ArbBot(whale_private_key)
    uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

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

    for token in base_assets:
        token_address = token["address"]
        token_contract = whale_arb_bot.web3.eth.contract(address=token_address, abi=erc20_abi)
        token_symbol = token_contract.functions.symbol().call()
        allowance = get_ERC20_allowance(token_contract, whale_address, uniswap_router_address)
        print(f"UniswapV2Router's allowance for {whale_address}'s {token_symbol}: {allowance} wei.")
        
