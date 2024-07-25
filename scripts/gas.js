async function queryAndUpdateGasParams() {
    const provider = ethers.getDefaultProvider('mainnet');
    const wallet = new ethers.Wallet('your-private-key', provider);
    const contractAddress = '0xYourContractAddress';
    const abi = [
        "function updateValue(uint256 newValue)"
    ];
    const contract = new ethers.Contract(contractAddress, abi, wallet);

    // Query current gas price and fee data
    const gasPrice = await provider.getGasPrice();
    const feeData = await provider.getFeeData();

    console.log('Current Gas Price:', gasPrice.toString());
    console.log('Fee Data:', feeData);

    // Estimate gas limit for the function call
    const estimatedGas = await contract.estimateGas.updateValue(42);
    const gasLimitWithBuffer = estimatedGas.add(estimatedGas.div(10)); // Adding 10% buffer

    console.log('Estimated Gas:', estimatedGas.toString());
    console.log('Gas Limit with Buffer:', gasLimitWithBuffer.toString());

    // Send the transaction with EIP-1559 gas parameters
    const tx = await contract.updateValue(42, {
        maxFeePerGas: feeData.maxFeePerGas,
        maxPriorityFeePerGas: ethers.utils.parseUnits('2.0', 'gwei'),  // Example priority fee
        gasLimit: gasLimitWithBuffer
    });

    console.log('Transaction:', tx);
}

queryAndUpdateGasParams().catch(console.error);
