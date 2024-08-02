import json
import os
from web3 import Web3
from utilities.populate_routes import (
    setup
    )
from utilities.approve_lp import (
    to_wei
)

def send_ETH_to_Arb(account, amount, arb_contract_address, web3, private_key):
  print('Sending ETH from account to arb contract...')
  # Send ETH to Contract
  tx = {
      'from': account.address,
      'to': arb_contract_address,
      'value': to_wei(amount, 18), 
      'gas': 400000, 
      'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
      'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
      'nonce': web3.eth.get_transaction_count(account.address),
      'chainId': web3.eth.chain_id
  }

  # Sign and send the transaction
  signed_tx = web3.eth.account.sign_transaction(tx, private_key)
  tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  return tx_receipt

def swap_ETH_for_USDT(web3, account, private_key, weth_instance, usdt_instance, router_instance, arb_contract):
  # Swaps ETH in account for USDT on router, and sends USDT to arb_contract.

  # Define swap parameters
  amount_in_wei = to_wei(1, 18)
  amount_out_min = to_wei(1500, 6)
  path = [weth_instance.address, usdt_instance.address]
  deadline = int(web3.eth.get_block('latest')['timestamp']) + 300  # 5 minutes from the current block time

  print('''--------------------------------
Wrapping ETH to WETH in account...''')
  # Wrap ETH to WETH
  nonce = web3.eth.get_transaction_count(account.address)
  wrap_tx = weth_instance.functions.deposit().build_transaction({
      'chainId': web3.eth.chain_id,
      'gas': 400000,
      'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
      'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
      'nonce': nonce,
      'value': amount_in_wei  # Amount of ETH to wrap into WETH
  })
  

  # Sign and send the wrapping transaction
  signed_wrap_tx = web3.eth.account.sign_transaction(wrap_tx, private_key)
  wrap_tx_hash = web3.eth.send_raw_transaction(signed_wrap_tx.rawTransaction)
  wrap_tx_receipt = web3.eth.wait_for_transaction_receipt(wrap_tx_hash)
  if wrap_tx_receipt['status'] == 1:
    print(f"Wrapped ETH on account: {weth_instance.functions.balanceOf(account.address).call()}")
  else:
    print('Wrap ETH to WETH failed.')

  print('''--------------------------------
Approving WETH allowance from account to router...''')
  # Approve the Uniswap router to spend WETH
  nonce += 1
  approve_tx = weth_instance.functions.approve(router_instance.address, amount_in_wei).build_transaction({
      'chainId': web3.eth.chain_id,
      'gas': 400000,
      'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
      'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
      'nonce': nonce,
  })

  # Sign and send the WETH approval transaction
  signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key)
  approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
  WETH_approval_receipt = web3.eth.wait_for_transaction_receipt(approve_tx_hash)
  if WETH_approval_receipt['status'] == 1:
    print(f"Current WETH allowance on router: {weth_instance.functions.allowance(account.address, router_instance.address).call()}")
  else:
    print('WETH approval failed.')

  print('''--------------------------------
Swapping WETH on account to USDT on arb contract...''')
  # Perform the swap
  nonce += 1
  swap_tx = router_instance.functions.swapExactETHForTokens(
      amount_out_min,
      path,
      arb_contract.address,
      deadline
  ).build_transaction({
      'chainId': web3.eth.chain_id,
      'gas': 400000,
      'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
      'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
      'nonce': nonce,
      'value': amount_in_wei,  # Amount of WETH to swap
  })

  # Sign and send the transaction
  signed_swap_tx = web3.eth.account.sign_transaction(swap_tx, private_key)
  swap_tx_hash = web3.eth.send_raw_transaction(signed_swap_tx.rawTransaction)
  swap_receipt = web3.eth.wait_for_transaction_receipt(swap_tx_hash)
  print(f"Current USDT balance on arb contract: {arb_contract.functions.getBalance(usdt_instance.address).call()}")
  return swap_receipt['status']

def read_all_functions(arb_contract):
  print(f'All functions of the arb contract: {arb_contract.all_functions()}')

def estimate_return(arb_contract):
  est_return = arb_contract.functions.estimateTradeReturn(
      _router1 = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
      _router2 = "0xEfF92A263d31888d860bD50809A8D171709b7b1c",
      _token1 = "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      _token2 = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      _amount = to_wei(10, 6)).call()
  return est_return

def execute_trade(arb_contract, router1_address, router2_address, token1_address, token2_address, amount, private_key):
  # test executeTrade(address,address,address,address,uint256)
  # Call executeTrade
  tx = arb_contract.functions.executeTrade(router1_address, router2_address, token1_address, token2_address, amount).build_transaction({
      'chainId': web3.eth.chain_id,
      'gas': 2000000,
      'maxFeePerGas': web3.to_wei('100', 'gwei'),  # Adjust these values according to network conditions
      'maxPriorityFeePerGas': web3.to_wei('5', 'gwei'),
      'nonce': web3.eth.get_transaction_count(account.address)
  })
  
  # Sign and send the transaction
  signed_trade_tx = web3.eth.account.sign_transaction(tx, private_key)
  trade_tx_hash = web3.eth.send_raw_transaction(signed_trade_tx.rawTransaction)
  receipt = web3.eth.wait_for_transaction_receipt(trade_tx_hash)

  # Check if the transaction was successful
  if receipt['status'] == 1:
    print("executeTrade function executed successfully")
  else:
    print("executeTrade function failed")

if __name__ == "__main__":
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
  private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
  account = web3.eth.account.from_key(private_key)

  uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
  uniswap_router_abi = '''
  [
      {
          "constant": false,
          "inputs": [
              {
                  "name": "amountOutMin",
                  "type": "uint256"
              },
              {
                  "name": "path",
                  "type": "address[]"
              },
              {
                  "name": "to",
                  "type": "address"
              },
              {
                  "name": "deadline",
                  "type": "uint256"
              }
          ],
          "name": "swapExactETHForTokens",
          "outputs": [
              {
                  "name": "amounts",
                  "type": "uint256[]"
              }
          ],
          "payable": true,
          "stateMutability": "payable",
          "type": "function"
      },
      {
          "constant": false,
          "inputs": [
              {
                  "name": "amountIn",
                  "type": "uint256"
              },
              {
                  "name": "amountOutMin",
                  "type": "uint256"
              },
              {
                  "name": "path",
                  "type": "address[]"
              },
              {
                  "name": "to",
                  "type": "address"
              },
              {
                  "name": "deadline",
                  "type": "uint256"
              }
          ],
          "name": "swapExactTokensForTokens",
          "outputs": [
              {
                  "name": "amounts",
                  "type": "uint256[]"
              }
          ],
          "payable": false,
          "stateMutability": "nonpayable",
          "type": "function"
      },
      {
          "constant": false,
          "inputs": [
              {
                  "name": "amountIn",
                  "type": "uint256"
              },
              {
                  "name": "amountOutMin",
                  "type": "uint256"
              },
              {
                  "name": "path",
                  "type": "address[]"
              },
              {
                  "name": "to",
                  "type": "address"
              },
              {
                  "name": "deadline",
                  "type": "uint256"
              }
          ],
          "name": "swapExactTokensForETH",
          "outputs": [
              {
                  "name": "amounts",
                  "type": "uint256[]"
              }
          ],
          "payable": false,
          "stateMutability": "nonpayable",
          "type": "function"
      }
  ]
  '''
  uniswap_router = web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

  pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
  USDC_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
  USDC_iCAN_address = "0xa9efDEf197130B945462163a0B852019BA529a66"

  USDT_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
  erc20_abi = '''
  [
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
                  "name": "success",
                  "type": "bool"
              }
          ],
          "payable": false,
          "stateMutability": "nonpayable",
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
                  "name": "success",
                  "type": "bool"
              }
          ],
          "payable": false,
          "stateMutability": "nonpayable",
          "type": "function"
      }
  ]
  '''
  usdt = web3.eth.contract(address=USDT_address, abi=erc20_abi)

  weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
  weth_abi = '''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'''
  weth = web3.eth.contract(address=weth_address, abi=weth_abi)

  # Return all functions of the contract
  read_all_functions(arb_contract)

  # Send 100 ETH to the arbitrage contract; see if tx_receipt.status returns 1
  assert send_ETH_to_Arb(account, 100, arb_contract_address, web3, private_key).status == 1

  # Get the balance of the smart contract
  balance = web3.eth.get_balance(arb_contract_address)
  print(f'Current balance of ETH on arb contract: {balance}')
  assert balance > 99, "Unexpected! Send 100 ETH failed!"

  # Swap 1 ETH for USDT in Uniswap V2
  assert swap_ETH_for_USDT(web3, account, private_key, weth, usdt, uniswap_router, arb_contract) == 1, "Unexpected! Swap WETH-USDT failed!"
  
  # test getBalance(address)
  print(f'USDT balance is now {arb_contract.functions.getBalance(USDT_address).call()}')

  # test owner()
  assert arb_contract.functions.owner().call({"from": owner_address})==owner_address, "Unexpected! owner() test failed"

  # test estimateTradeReturn(address,address,address,address,uint256)
  assert estimate_return(arb_contract) == 6412564, "Unexpected! Estimated return wrong!"

  # test executeTrade(address,address,address,address,uint256) Error to fix
  print(f'{execute_trade(arb_contract, uniswap_router_address, pancake_router_address, USDT_address, USDC_address, to_wei(10, 6), private_key)}')
  #assert execute_trade(arb_contract, uniswap_router_address, pancake_router_address, USDT_address, USDC_address, to_wei(10, 6), private_key) == 1, "Unexpected! executeTrade() test failed"

  # test withdrawETH()

  # test withdrawToken(address)
