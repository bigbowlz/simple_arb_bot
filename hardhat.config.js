require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config({ path: '.env' });
require("@nomicfoundation/hardhat-ignition-ethers");
require("@nomicfoundation/hardhat-verify");
require("@nomiclabs/hardhat-ethers");

const { vars } = require("hardhat/config");
const ETHERSCAN_API_KEY = vars.get("ETHERSCAN_API_KEY");
const BSCSCAN_API_KEY = vars.get("BSCSCAN_API_KEY");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
    bsc_testnet: {
      url: process.env.BSC_TESTNET_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
    hardhat: {
      forking: {
        url: 'https://eth.llamarpc.com',
        blockNumber: 20283224,
      },
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
  },
  etherscan: {
    apiKey: {
        mainnet: ETHERSCAN_API_KEY,
        sepolia: ETHERSCAN_API_KEY,
        bsc: BSCSCAN_API_KEY,
        bscTestnet: BSCSCAN_API_KEY,
    }
  },
  sourcify: {
    // Disabled by default
    // Doesn't need an API key
    enabled: true
  }
};
