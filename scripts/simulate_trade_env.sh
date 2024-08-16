# Check if the port is now running the node
PORT=8545
if lsof -i:$PORT; then
    # Define the commands as variables
    whale="python3 trading_env_sims/whale_trading.py"
    whale_erc20="python3 trading_env_sims/whale_erc20_trading.py"
    regular="python3 trading_env_sims/regular_trading.py"
    regular_erc20="python3 trading_env_sims/regular_erc20_trading.py"
    current_dir=$(pwd)
    new_whale_erc20="cd ${current_dir} && ${whale_erc20}"
    new_regular="cd ${current_dir} && ${regular}"
    new_regular_erc20="cd ${current_dir} && ${regular_erc20}"

    # Open a new shell and run the commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        ${whale} & 
        osascript -e "tell application \"Terminal\" to do script \"${new_whale_erc20}\"" &
        osascript -e "tell application \"Terminal\" to do script \"${new_regular}\"" &
        osascript -e "tell application \"Terminal\" to do script \"${new_regular_erc20}\"" 
    else
        echo "Unsupported OS"
    fi
else
    echo "Node not initialized for the Ethereum fork."
fi