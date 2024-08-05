from web3 import Web3
from utilities.balances import (sign_and_send_tx)
'''
arb_bot.py

Models the on-chain smart contract so that all on-chain functions can be easily called off-chain, 
while providing some additional functions to get network gas consumption details. 
Maintains arbitrage trading states like profitability and slippage settings.

Author: ILnaw
Version: 08-04-2024
'''

class ArbBot:
    """
    Represents an arbitrage bot contract.

    Attributes:
        node_url (str): The url of the node.
        web3 (Provider): A Provider instance to access blockchain. Takes JSON-RPC requests and return the response.
        chain_id (int): The ID of the connected chain.
        private_key (str): Hex value of a private key.
        sender_address (str): Address of the sender.
        bot_address (str): Address of the arbitrage bot contract.
        bot_abi (str): abi of the arbitrage bot contract.
        bot (Contract): Contract instance of the arbitrage bot contract.
        min_profitBP (int): Basis point value of the minimum profitability accepted in a trade that's smaller than profit/(liquidity + gas).
        slippage_bufferBP (int): Basis point value of the slippage buffer percentage added for swaps.
    """
    def __init__(self, min_profitBP, slippage_bufferBP, private_key, bot_address='0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94'):
        """
        Initialize the ArbBot instance with the minimum profitability BP, the slippage buffer for swaps, the private key of the sender address, and the deployed arbitrage bot contract address.

        Params:
            min_profitBP (int): Basis point value of the minimum profitability accepted in a trade that's smaller than profit/(liquidity + gas).
            slippage_bufferBP (int): Basis point value of the slippage buffer percentage added for swaps.
            private_key (str): Hex value of a private key.
            bot_address (str): Address of the arbitrage bot contract.
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
        """
        Executes an arbitrage trade that swaps a specified amount of token1 to token2 on router1, and from token2 to token1 on router2.
        
        Params:
            router1 (str): The address of a router contract.
            router2 (str): The address of a router contract.
            token1 (str): The address of a token contract.
            token2 (str): The address of a token contract.
            amount (int): The amount of token1 to trade with.

        Returns:
            none
        """
        tx = self.bot.functions.executeTrade(
            router1, router2, token1, token2, amount
            ).build_transaction(self.build_tx('executeTrade', router1, router2, token1, token2, amount))
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)
        
        if receipt['status'] == 1:
            print("executeTrade() succeeded! Arb trade completed.")
        else:
            print("executeTrade() failed! Arb trade failed.")
    
    def estimate_return(self, router1, router2, token1, token2, amount):
        """
        Estimates the return of an arbitrage trade that swaps a specified amount of token1 to token2 on router1, and from token2 to token1 on router2.
        
        Params:
            router1 (str): The address of a router contract.
            router2 (str): The address of a router contract.
            token1 (str): The address of a token contract.
            token2 (str): The address of a token contract.
            amount (int): The amount of token1 to trade with.

        Returns:
            The estimated amount of return in token2. 
        """

        est_return = self.bot.functions.estimateTradeReturn(
            _router1 = router1,
            _router2 = router2,
            _token1 = token1,
            _token2 = token2,
            _amount = amount).call()
        return est_return

    def get_balance(self, address):
        """
        Gets the balance of a token in the arbitrage contract.

        Params:
            address (str): The address of a token contract.

        Returns:
            (int): The wei amount of the token balance.
        """
        return self.bot.functions.getBalance(address).call()
    
    def get_owner(self):
        """
        Gets the owner contract of the arbitrage contract.

        Returns:
            (str): The address of the arbitrage contract owner.
        """
        return self.bot.functions.owner().call()
    
    def withdraw_eth(self):
        """
        Withdraw all ETH balance from the arbitrage contract to the owner account.

        Returns:
            (receipt): The receipt of the ETH withdrawal transaction. 
        """
        tx = self.bot.functions.withdrawETH().build_transaction(
            self.build_tx('withdrawETH'))
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)
        return receipt
    
    def withdraw_token(self, token_address):
        """
        Withdraw all balance of a token from the arbitrage contract to the owner account.

        Returns:
            (receipt): The receipt of the token withdrawal transaction. 
        """
        tx = self.bot.functions.withdrawToken(token_address).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'maxFeePerGas': self.web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
            'maxPriorityFeePerGas': self.web3.to_wei('5', 'gwei'),
            'nonce': self.get_sender_nonce(),
            'from': self.sender_address
            })
        
        receipt = sign_and_send_tx(self.web3, tx, self.private_key)

        return receipt

    def get_min_profitBP(self):
        """
        Returns the minimum profitability BP. 
        Returns:
            (int): the minimum profitability BP.
        """
        return self.min_profitBP

    def set_min_profitBP(self, min_profitBP):
        """
        Sets the minimum profitability BP. 

        Param:
            min_profitBP (int): the minimum profitability BP.

        Returns:
            none
        """
        self.min_profitBP = min_profitBP

    def get_slippage_bufferBP(self):
        """
        Returns the swap slippage buffer BP. 

        Returns:
            (int): the swap slippage buffer BP.
        """
        return self.slippage_bufferBP

    def set_slippage_bufferBP(self, slippage_bufferBP):
        """
        Sets the swap slippage buffer BP. 

        Param:
            slippage_bufferBP (int): the swap slippage buffer BP.

        Returns:
            none
        """
        self.slippage_bufferBP = slippage_bufferBP

    def get_max_feePerGas(self):
        """
        Returns the latest MaxFeePerGas on the network.

        Returns:
            (int): the latest MaxFeePerGas on the network. 
        """
        base_fee_per_gas = self.web3.eth.get_block('latest')['baseFeePerGas']
        max_priority_fee_per_gas = self.web3.eth.max_priority_fee
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

        print(f"Base Fee per Gas: {base_fee_per_gas}")
        print(f"Max Priority Fee per Gas: {max_priority_fee_per_gas}")
        print(f"Max Fee per Gas: {max_fee_per_gas}")

        return max_fee_per_gas

    def estimate_function_gas(self, func_to_call, *args):
        """
        Returns the gas estimate of an arbitrage bot contract function.
        
        Params:
            func_to_call (str): the name of the function to call.
            *args: arguments of the func_to_call as in the contract function definition.

        Returns:
            (int): Estimated gas cost of the arbitrage contract function call lifted by 1.3 times.
        """
        # Get the function object from the bot contract
        contract_func = self.bot.functions[func_to_call](*args)
        
        # Estimate gas of an on-chain function call
        gas_estimate = contract_func.estimate_gas({
            'from': self.sender_address
        })

        return 1.3 * gas_estimate # adjust amplifier based on network competition
    
    def get_sender_nonce(self):
        """
        Returns the nonce of the sender in transaction count.
        
        Returns:
            (int): the nonce of the sender in transaction count.
        """
        return self.web3.eth.get_transaction_count(self.sender_address)
    
    def build_tx(self, func_to_call, *args):
        """
        Builds a transaction for an arbitrage bot contract function call.
        
        Params:
            func_to_call (str): the name of the function to call.
            *args: arguments of the func_to_call as in the contract function definition.

        Returns:
            tx(dict): the dictionary representation of a transaction.
        """
        gas = int(self.estimate_function_gas(func_to_call, *args)) + 100
        print(f'gas estimate for {func_to_call} is: {gas}')
        tx = {
            'chainId': self.chain_id,
            'gas': gas,
            'maxFeePerGas': self.get_max_feePerGas()*2,
            'nonce': self.get_sender_nonce()
        }
        return tx