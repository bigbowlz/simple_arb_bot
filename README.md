# Simple Arb Bot 
This project aims to develop an automated arbitrage bot for Uniswap V2 DEXes and profit from the price differences of the same asset in different DEX markets. This bot will collect live price of a list of assets from on-chain smart contracts, and make informed decisions about when to execute simultaneous arbitrage transactions. The ultimate goal is to profit from these transactions while contributing to the overall efficiency and balance of DeFi markets by aligning prices across different markets or exchanges. 

## Project Setup
### Install Dependencies
To host an Ethereum fork locally and deploy arbitrage contracts

    npm install --save-dev hardhat 
    npm install --save-dev @nomicfoundation/hardhat-toolbox
    npm install --save-dev @nomicfoundation/hardhat-ethers
    
To connect to Ethereum using web3.py

    pip install web3
    pip install python-dotenv

To install contract libraries

    npm install @openzeppelin/contracts
    npm install @uniswap/v2-periphery


To manage environment variables

    npm install dotenv


### Set up the trading environment on Terminal
#### Start a local Ethereum folk, deploy the arbitrage contract, set up token liquidity in the arb contract, and populate valid trade routes. Run the command from the root directory.
```
chmod +x scripts/env_setup.sh && ./scripts/env_setup.sh
```

#### Deployed addresses after setup:
    arbitrage#Arbitrage - 0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94
    BTC#BTC_iCAN - 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
    USDC#USDC_iCAN - 0xa9efDEf197130B945462163a0B852019BA529a66

    addresses used for trading:
    WARNING: These accounts, and their private keys, are publicly known.
    Any funds sent to them on Mainnet or any other live network WILL BE LOST.

    bot owner account
    Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
    Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

    whale trader account (Whale trader simulator that trades ETH for ERC20)
    Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
    Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

    regular trader account (Regular trader simulator that trades ETH for ERC20)
    Account #2: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (10000 ETH)
    Private Key: 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

    whale erc20 trader account (Whale trader simulator that trades ERC20 for ERC20)
    Account #3: 0x90F79bf6EB2c4f870365E785982E1f101E93b906 (10000 ETH)
    Private Key: 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6

    regular erc20 trader account (Regular trader simulator that trades ERC20 for ERC20)
    Account #4: 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65 (10000 ETH)
    Private Key: 0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a
## Run the arb bot
#### Run the arb bot, and log the balances of all tokens in the arbitrage contract in `balance_logs.csv`. Run the command from the root directory.
```
chmod +x scripts/run_bot.sh && ./scripts/run_bot.sh
```

## Simulate live trading environment with whale traders and regular traders
```
chmod +x scripts/simulate_trade_env.sh && ./scripts/simulate_trade_env.sh
```