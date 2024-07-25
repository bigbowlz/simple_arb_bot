# Project Setup

## Install Dependencies
To host an Ethereum fork locally and deploy arbitrage contracts

    npm install --save-dev hardhat 
    npm install @nomicfoundation/hardhat-toolbox

To connect to Ethereum using web3.py

    pip install web3

To install contract libraries

    npm install @openzeppelin/contracts
    npm install @uniswap/v2-periphery


To manage environment variables

    npm install dotenv


## Terminal 1
#### Start a locally hosted Ethereum fork: 
    npx hardhat compile
    npx hardhat node


## Terminal 2
#### Deploy the arbitrage contract and test tokens USDC iCAN and BTC iCAN:
    npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost
    npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost
    npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost

#### Deployed addresses after setup:
    Default signer - 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
    arbitrage#Arbitrage - 0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94
    BTC#BTC_iCAN - 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
    USDC#USDC_iCAN - 0xa9efDEf197130B945462163a0B852019BA529a66

#### Generate ABI files for on-chain router contracts (Uniswap, PancakeSwap, and SushiSwap):
    python utilities/populate_routes.py --ABI
    
#### Iterate through tokens and routers in the config file to find valid routes:
    python utilities/populate_routes.py --route

#### Approve USDC iCAN and BTC iCAN for routers and create a liquidity pool
    npx hardhat run scripts/approveTokenAndLP.js