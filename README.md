# Project Setup

## Install Dependencies
To host an Ethereum fork locally and deploy arbitrage contracts

    npm install --save-dev hardhat 
    npm install @nomicfoundation/hardhat-toolbox
    npm install @nomicfoundation/hardhat-ethers@3.0.6
    
To connect to Ethereum using web3.py

    pip install web3

To install contract libraries

    npm install @openzeppelin/contracts
    npm install @uniswap/v2-periphery


To manage environment variables

    npm install dotenv


## Terminal
#### Run the setup script to start a local Ethereum folk, deploy test tokens and the arbitrage contract, and populate valid trade routes.
```
chmod +x scripts/setup.sh && ./scripts/setup.sh
```