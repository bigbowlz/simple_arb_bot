# Project Setup

## Install Dependencies
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


## Terminal
#### Run the setup script to start a local Ethereum folk, deploy test tokens and the arbitrage contract, and populate valid trade routes.
```
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

#### Deployed addresses after setup:
    Default signer - 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
    arbitrage#Arbitrage - 0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94
    BTC#BTC_iCAN - 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
    USDC#USDC_iCAN - 0xa9efDEf197130B945462163a0B852019BA529a66