async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  //const initialSupplyBTC_iCAN = ethers.utils.parseUnits("1000_000_000_000", 8); // BTC is 8 decimal
  const Token_BTC = await ethers.getContractFactory("BTC_iCAN");
  const token_BTC = await Token_BTC.deploy(1000_000_000_000);
  console.log("BTC_iCAN:", token_BTC.address);

  //const initialSupplyUSDC_iCAN = ethers.utils.parseUnits("1000_000_000", 6); // USDC is 6 decimal
  const Token_USDC = await ethers.getContractFactory("USDC_iCAN");
  const token_USDC = await Token_USDC.deploy(1000_000_000_000_000);
  console.log("USDC_iCAN:", token_USDC.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
