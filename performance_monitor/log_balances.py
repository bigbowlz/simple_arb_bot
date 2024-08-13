from utilities.trading_utilities import (get_account_balances)
from datetime import datetime
from utilities.arb_bot import ArbBot
import time
import csv
import json
'''
log_balances.py

Logs the balance of all tokens in the arb contract during the operation of an ArbBot
according to the interval configged.

Author: ILnaw
Version: 08-14-2024
'''     
def log_balance_to_csv(arb_bot, end_time, interval):
    """
    Logs the balance of all tokens in the arb contract every 5 minutes during operation.

    Params:
        arb_bot (ArbBot): An ArbBot instance.
        end_time (float): the end_time of the balancing logging.
        interval (int): the interval of logging in seconds.
    """
    with open("performance_monitor/balance_logs.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "ETH", "USDT", "USDC", "WBTC", "SHIB", "DAI"])
        
    while time.time() < end_time:
        with open("performance_monitor/balance_logs.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            balances = get_account_balances(arb_bot.web3, arb_bot.bot_address)
            writer.writerow([
                current_time, 
                balances["ETH"], 
                balances["USDT"],
                balances["USDC"],
                balances["WBTC"],
                balances["SHIB"],
                balances["DAI"]
                ])
        time.sleep(interval) 

if __name__ == "__main__":
    with open('opportunity_analysis/arb_bot_config.json', 'r') as arb_bot_config_file:
        arb_bot_config = json.load(arb_bot_config_file)

    min_profitBP = arb_bot_config["min_profitBP"]
    slippage_bufferBP = arb_bot_config["slippage_bufferBP"]
    duration = arb_bot_config["duration"]
    start_time = arb_bot_config["start_time"]
    PRIVATE_KEY = arb_bot_config["PRIVATE_KEY"]
    arb_bot = ArbBot(min_profitBP, slippage_bufferBP, PRIVATE_KEY)
    
    log_balance_to_csv(arb_bot, start_time+duration, 60)