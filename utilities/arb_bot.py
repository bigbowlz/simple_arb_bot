'''
arb_bot.py

Models the on-chain smart contract so that all on-chain functions can be easily called off-chain, 
while providing some additional functions to get network gas consumption details. 
Maintains arbitrage trading states like profitability and slippage settings.

Author: ILnaw
Version: 0.0.1
'''
from web3 import Web3
from balances import (to_wei, from_wei, sign_and_send_tx)

class ArbBot:
    def __init__(self, min_profitBP, slippage_bufferBP, private_key, bot_address='0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94'):
        """
        Initialize the ArbBot class.
        """
        # Connect to localhost
        self.node_url = "http://127.0.0.1:8545"
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))
        self.chain_id = self.web3.eth.chain_id

        if not self.web3.is_connected():
            raise Exception("Unable to connect to localhost")
        
        # Convert private key to public key
        self.private_key = private_key
        signer_wallet = self.web3.eth.account.from_key(self.private_key)
        self.sender_address = signer_wallet.address

        # Create a bot contract web3 instance
        self.bot_address = bot_address 
        self.bot_abi = [
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
        self.bot = self.web3.eth.contract(address=self.bot_address, abi=self.bot_abi)

        self.min_profitBP = min_profitBP
        self.slippage_bufferBP = slippage_bufferBP
    
    def execute_trade(self, router1, router2, token1, token2, amount):
        tx = self.bot.functions.executeTrade(
            router1, router2, token1, token2, amount
            ).build_transaction(self.build_tx('executeTrade', router1, router2, token1, token2, amount))
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)
        
        if receipt['status'] == 1:
            print("executeTrade() succeeded! Arb trade completed.")
        else:
            print("executeTrade() failed! Arb trade failed.")
    
    def estimate_return(self, router1, router2, token1, token2, amount):
        est_return = self.bot.functions.estimateTradeReturn(
            _router1 = router1,
            _router2 = router2,
            _token1 = token1,
            _token2 = token2,
            _amount = amount).call()
        return est_return

    def get_balance(self, address):
        return self.bot.functions.getBalance(address).call()
    
    def get_owner(self):
        return self.bot.functions.owner().call()
    
    def withdraw_eth(self):
        tx = self.bot.functions.withdrawETH().build_transaction(
            self.build_tx('withdrawETH'))
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)
        return receipt
    
    def withdraw_token(self, token_address):
        tx = self.bot.functions.withdrawToken(token_address).build_transaction({
            'chainId': self.chain_id,
            'gas': 1000000,
            'maxFeePerGas': self.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
            'maxPriorityFeePerGas': self.web3.to_wei('5', 'gwei'),
            'nonce': self.get_sender_nonce()
            })
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)

        return receipt

    def get_min_profitBP(self):
        return self.min_profitBP

    def set_min_profitBP(self, min_profitBP):
        self.min_profitBP = min_profitBP

    def get_slippage_bufferBP(self):
        return self.slippage_bufferBP

    def set_slippage_bufferBP(self, slippage_bufferBP):
        self.slippage_bufferBP = slippage_bufferBP

    def get_max_feePerGas(self):
        base_fee_per_gas = self.web3.eth.get_block('latest')['baseFeePerGas']
        max_priority_fee_per_gas = self.web3.eth.max_priority_fee
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

        print(f"Base Fee per Gas: {base_fee_per_gas}")
        print(f"Max Priority Fee per Gas: {max_priority_fee_per_gas}")
        print(f"Max Fee per Gas: {max_fee_per_gas}")

        return max_fee_per_gas

    def __estimate_function_gas(self, func_to_call, *args):
        # Get the function object from the bot contract
        contract_func = self.bot.functions[func_to_call](*args)
        
        # Estimate gas of an on-chain function call
        gas_estimate = contract_func.estimate_gas({
            'from': self.sender_address
        })

        return 1.3 * gas_estimate # adjust amplifier based on network competition
    
    def get_sender_nonce(self):
        return self.web3.eth.get_transaction_count(self.sender_address)
    
    def build_tx(self, func_to_call, *args):
        tx = {
            'chainId': self.chain_id,
            'gas': self.__estimate_function_gas(func_to_call, *args),
            'maxFeePerGas': self.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
            'maxPriorityFeePerGas': self.web3.to_wei('5', 'gwei'),
            'nonce': self.get_sender_nonce()
        }
        return tx