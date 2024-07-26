# Run the script using: chmod +x scripts/setup.sh && ./scripts/setup.sh

# Check if port 8545 is in use and kill the process if found
PORT=8545
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Port $PORT is in use by PID $PID. Terminating process..."
    kill -9 $PID
    echo "Process terminated."
fi

# Start a locally hosted Ethereum fork
npx hardhat node &

# Check if the node started successfully
sleep 5  # Give it some time to start

if [ $? -eq 0 ]; then
    # Get the current working directory
    current_dir=$(pwd)

    # Define the commands as variables
    abi="python utilities/populate_routes.py --ABI" # Generate ABI files for on-chain router contracts (Uniswap, PancakeSwap, and SushiSwap)
    route="python utilities/populate_routes.py --route" # Iterate through tokens and routers in the config file to find valid routes
    compile="npx hardhat compile" # Compile contracts 
    deploy="npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost && npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost && npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost" #Deploy the arbitrage contract and test tokens USDC iCAN and BTC iCAN
    pool="npx hardhat run scripts/approveTokenAndLP.js" # Approve USDC iCAN and BTC iCAN for routers and create a liquidity pool

    # Open a new terminal window and run the commands
    # osascript -e "tell application \"Terminal\" to do script \"cd ${current_dir} && ${abi} && ${route} && ${compile} && ${deploy} && ${pool}\""
    osascript -e "tell application \"Terminal\" to do script \"cd ${current_dir} && ${compile} && ${deploy} && ${abi}\""

else
    echo "Node initialization failed for the Ethereum fork."
fi