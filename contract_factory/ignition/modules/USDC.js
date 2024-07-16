const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const USDCModule = buildModule("USDC", (m) => {
  const initialSupply = BigInt("1000000000000000");
  const token = m.contract("USDC_iCAN", [initialSupply]);

  return { token };
});

module.exports = USDCModule;