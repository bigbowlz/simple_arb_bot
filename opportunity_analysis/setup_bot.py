import time
import json
from utilities.arb_bot import ArbBot
'''
setup_bot.py

Asks for user input for the configs including min_profitBP, slippage_bufferBP and operation duration to set up an ArbBot instance.
Stores the configs to a json file for parallel uses in other processes.
'''
def config_bot(private_key):
    """
    Configs the arb bot instance with min_profitBP, slippage_bufferBP and operation duration.

    Returns:
        arb_bot (ArbBot): an ArbBot instance.
        duration (int): duration of operation in minutes.

    """
    use_default_min_profitBP = input("Use default min_profitBP (500 bps)? (y/n)")
    if use_default_min_profitBP in ["y", "Y", "yes", "Yes"]:
        min_profitBP = 500
    else:
        min_profitBP = int(input("Min profitability target in bps: "))

    use_default_slippage_bufferBP = input("Use default slippage_bufferBP (100 bps)? (y/n)")
    if use_default_slippage_bufferBP in ["y", "Y", "yes", "Yes"]:
        slippage_bufferBP = 100
    else:
        slippage_bufferBP = int(input("Slippage buffer in bps:"))

    print('Initiating the arbitrage bot...')
    arb_bot = ArbBot(private_key, min_profitBP=min_profitBP, slippage_bufferBP=slippage_bufferBP)

    use_default_minutes = input("Use default minutes (30 mins)? (y/n)")
    if use_default_minutes in ["y", "Y", "yes", "Yes"]:
        minutes = 30
    else:
        minutes = int(input('Operation duration in minutes: '))

    return arb_bot, minutes

if __name__ == "__main__":
    start_time = time.time() 
    PRIVATE_KEY = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80' # this is known to public
    arb_bot, minutes = config_bot(PRIVATE_KEY)
    duration = minutes * 60 # seconds to operate the bot    
    min_profitBP = arb_bot.get_min_profitBP()
    slippage_bufferBP = arb_bot.get_slippage_bufferBP()
    arb_bot_config = {
        "min_profitBP": min_profitBP,
        "slippage_bufferBP": slippage_bufferBP,
        "duration": duration,
        "start_time": start_time,
        "PRIVATE_KEY": PRIVATE_KEY
    }
    with open('opportunity_analysis/arb_bot_config.json', 'w') as arb_bot_config_file:
        json.dump(arb_bot_config, arb_bot_config_file, indent=4)