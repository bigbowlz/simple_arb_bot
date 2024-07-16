'''
balances.py

Gets and logs the balance of an asset in an account. 
Called in trade.py as an argument to executeTrade as a trade can only succeed 
when there's enough balance of the baseAsset in the user wallet.

Author: ILnaw
Version: 0.0.1
'''

def get_token_balance(accountAddress, assetAddress):
    '''
    Gets and logs the balance of an asset in an account. 
    '''
    return {} #{assetAddress: balance}

