# cmd setup script
'''
cd simple_arb_bot/contract_factory
npx hardhat node
cd simple_arb_bot/contract_factory
npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost
npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost
npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost

'''