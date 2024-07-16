const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("arbitrage", (m) => {
  const arbitrage = m.contract("Arbitrage", {
  });

  return { arbitrage };
});