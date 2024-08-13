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
    Default signer - 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
    arbitrage#Arbitrage - 0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94
    BTC#BTC_iCAN - 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
    USDC#USDC_iCAN - 0xa9efDEf197130B945462163a0B852019BA529a66

## Run the arb bot
#### Run the arb bot, and log the balances of all tokens in the arbitrage contract in `balance_logs.csv`. Run the command from the root directory.
```
chmod +x scripts/run_bot.sh && ./scripts/run_bot.sh
```