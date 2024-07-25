const { ethers } = require("hardhat");

async function approveTokens(tokenAddress, spenderAddress, amount) {
    const [owner] = await ethers.getSigners();
    const token = new ethers.Contract(tokenAddress, [
        "function approve(address spender, uint256 amount) public returns (bool)"
    ], owner);    
    
    console.log(`Approving ${amount.toString()} of token ${tokenAddress} to spender ${spenderAddress}`);
    const tx = await token.approve(spenderAddress, amount);
    await tx.wait();
    console.log(`Approved ${amount} of token ${tokenAddress} to spender ${spenderAddress}`);
}

async function createPool(routerAddress, tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin) {
    const [owner] = await ethers.getSigners();
    const router = new ethers.Contract(routerAddress, [
        "function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) public returns (uint amountA, uint amountB, uint liquidity)"
    ], owner);
    
    const deadline = Math.floor(Date.now() / 1000) + 60 * 20; //Deadline is set as 20 mins from now
    
    console.log(`Adding liquidity with the following parameters:
        tokenA: ${tokenA}
        tokenB: ${tokenB}
        amountADesired: ${amountADesired.toString()}
        amountBDesired: ${amountBDesired.toString()}
        amountAMin: ${amountAMin.toString()}
        amountBMin: ${amountBMin.toString()}
        to: ${owner.address}
        deadline: ${deadline}`);
    
        
    try {
        const gasLimit = await router.estimateGas.addLiquidity(
            tokenA,
            tokenB,
            amountADesired,
            amountBDesired,
            amountAMin,
            amountBMin,
            owner.address,
            deadline
        );

        const tx = await router.addLiquidity(
            tokenA,
            tokenB,
            amountADesired,
            amountBDesired,
            amountAMin,
            amountBMin,
            owner.address,
            deadline,
            { gasLimit: gasLimit.add(ethers.BigNumber.from('100000')) } // Adding a buffer
        );
        await tx.wait();
        console.log(`Liquidity added successfully to router ${routerAddress}`);
    } catch (error) {
        console.error("Error while trying to add liquidity: ", error);
    }
}

async function main() {
    const uniswap = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"; // Uniswap V2 Router address

    const BTC_iCAN = "0x49AeF2C4005Bf572665b09014A563B5b9E46Df21";
    const USDC_iCAN = "0xa9efDEf197130B945462163a0B852019BA529a66";
    
    try {
        const amountBTCApprove = ethers.utils.parseUnits("200", 8); // Amount to approve
        const amountUSDCApprove = ethers.utils.parseUnits("10000000", 6); // Amount to approve

        await approveTokens(BTC_iCAN, uniswap, amountBTCApprove);
        await approveTokens(USDC_iCAN, uniswap, amountUSDCApprove);
    } catch (error) {
        console.error("Error while trying to approve token: ", error);
    }
    
    try {
        const amountBTCLP = ethers.utils.parseUnits("100", 8); // Amount to add liquidity with
        const amountBTCLPMin = ethers.utils.parseUnits("90", 8); // Min amount to add liquidity with
    
        const amountUSDCLP = ethers.utils.parseUnits("5000000", 6); // Amount to add liquidity with
        const amountUSDCLPMin = ethers.utils.parseUnits("4000000", 6) // Min amount to add liquidity with
        
        await createPool(uniswap, BTC_iCAN, USDC_iCAN, amountBTCLP, amountUSDCLP, amountBTCLPMin, amountUSDCLPMin);
    } catch (error) {
        console.error("Error while trying to createPool: ", error);
    }
}

main().catch((error) => {
    console.error("Error in script execution: ", error);
    process.exitCode = 1;
});