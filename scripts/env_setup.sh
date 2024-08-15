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

# Check if the port is now in use
if lsof -i:$PORT; then
    # Get the current working directory
    current_dir=$(pwd)

    # Define the commands as variables
    checksum="python utilities/populate_routes.py --checksum"
    compile="npx hardhat compile" # Compile contracts 
    deploy="npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost && npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost && npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost" #Deploy the arbitrage contract and test tokens USDC iCAN and BTC iCAN
    pool="python utilities/approve_lp.py" # Approve USDC iCAN and BTC iCAN for routers and create a liquidity pool
    abi="python utilities/populate_routes.py --ABI" # Generate ABI files for on-chain router contracts (Uniswap and SushiSwap)
    route="python utilities/populate_routes.py --route" # Iterate through tokens and routers in the config file to find valid routes
    setup_liq="python scripts/arb_liquidity_setup.py" # Set up liquidity for all baseAssets in the arb contract
    commands="cd ${current_dir} && ${checksum} && ${compile} && ${deploy} && ${pool} && ${abi} && ${route} && ${setup_liq}"

    # Open a new shell and run the commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"${commands}\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        # Windows with WSL
        cmd.exe /c start wsl.exe bash -c "cd ${current_dir} && \
            python3 utilities/populate_routes.py --checksum && \
            npx hardhat compile && \
            npx hardhat ignition deploy ./ignition/modules/arbitrage.js --network localhost && \
            npx hardhat ignition deploy ./ignition/modules/BTC.js --network localhost && \
            npx hardhat ignition deploy ./ignition/modules/USDC.js --network localhost && \
            python utilities/approve_lp.py && \
            python3 utilities/populate_routes.py --ABI && \
            python3 utilities/populate_routes.py --route && \ 
            python scripts/arb_liquidity_setup.py
            "

    else
        echo "Unsupported OS"
    fi
else
    echo "Node initialization failed for the Ethereum fork."
fi