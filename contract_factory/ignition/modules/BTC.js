const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const BTCModule = buildModule("BTC", (m) => {
  const initialSupply = BigInt("1000000000000");
  const token = m.contract('BTC_iCAN', [initialSupply])
  return {token};
});

module.exports = BTCModule;