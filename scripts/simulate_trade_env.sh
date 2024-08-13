# Check if the port is now running the node
PORT=8545
if lsof -i:$PORT; then
    # Define the commands as variables
    whale="python3 trading_env_sims/whale_trading.py"
    regular="python3 trading_env_sims/regular_trading.py" # run the trading bot
    current_dir=$(pwd)
    commands="cd ${current_dir} && ${regular}"
    # Open a new shell and run the commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        ${whale} & 
        osascript -e "tell application \"Terminal\" to do script \"${commands}\""
    else
        echo "Unsupported OS"
    fi
else
    echo "Node not initialized for the Ethereum fork."
fi