# cmd setup script
'''
Terminal 1 cmds:
cd contract_factory
npx hardhat node

Terminal 2 cmds:
cd contract_factory
npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost
npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost
npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost

Deployed address should be:
arbitrage#Arbitrage - 0x00B0517de6b2b09aBD3a7B69d66D85eFdb2c7d94
BTC#BTC_iCAN - 0x49AeF2C4005Bf572665b09014A563B5b9E46Df21
USDC#USDC_iCAN - 0xa9efDEf197130B945462163a0B852019BA529a66

Default signer: 
0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

'''