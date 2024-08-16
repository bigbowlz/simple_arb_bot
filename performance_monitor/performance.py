import pandas as pd
import json
from web3.datastructures import AttributeDict

df = pd.read_csv("experiment_logs/08162324/trade_logs_bot.csv")
first_tx_receipt = df.loc[1, "tx_receipt"][14:-1]
first_tx_dict = json.loads(first_tx_receipt)
first_tx_receipt = AttributeDict(first_tx_dict)

print(first_tx_receipt['gasUsed'])