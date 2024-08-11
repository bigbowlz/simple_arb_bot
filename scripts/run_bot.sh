# Check if the port is now running the node
PORT=8545
if lsof -i:$PORT; then
    # Get the current working directory
    current_dir=$(pwd)

    # Define the commands as variables
    setup="python3 opportunity_analysis/setup_bot.py"
    trade="python3 opportunity_analysis/trade.py" # run the trading bot
    log_balances="python3 performance_monitor/log_balances.py" # log balances according to intervals defined

    # Open a new shell and run the commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        ${setup} &&
        (${trade} & ${log_balances})
    else
        echo "Unsupported OS"
    fi
else
    echo "Node not initialized for the Ethereum fork."
fi