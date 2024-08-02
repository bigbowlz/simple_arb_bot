'''
balances.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 0.0.1
'''

from populate_routes import (setup)

def get_ERC20_balance(accountAddress, assetAddress):
    '''
    Gets and logs the balance of an asset in an account. 
    '''
    return {} #{assetAddress: balance}

def get_ETH_balance(accountAddress, assetAddress):
