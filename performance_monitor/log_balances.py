from utilities.balances import (get_account_balances)
from datetime import datetime
from data_collection&analysis.trade import (arb_bot, start_time, duration)
import time
import csv

'''
log_balances.py

Logs the balance of all tokens in the arb contract every 5 minutes during the operation of an ArbBot.


Author: ILnaw
Version: 0.0.5
'''     
def log_balance_to_csv(arb_bot, end_time, interval):
    """
    Logs the balance of all tokens in the arb contract every 5 minutes during operation.

    Params:
        arb_bot: An ArbBot instance.
        end_time: the end_time of the balancing logging.
        interval: the interval of logging in seconds.
    """
    with open("balance_logs.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "ETH", "USDT", "USDC", "WBTC", "SHIB", "DAI"])
        
        while time.time() < end_time:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            balances = get_account_balances(arb_bot)
            writer.writerow([
                current_time, 
                balances["ETH"], 
                balances["USDT"],
                balances["USDC"],
                balances["WBTC"],
                balances["SHIB"],
                balances["DAI"]
                ])
            time.sleep(interval)  # Log every 5 minutes

if __name__ == "__main__":
    log_balance_to_csv(arb_bot, start_time+duration, 60)