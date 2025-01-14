import pandas as pd
from datetime import datetime as dt, timedelta as tmd

period_dict = {
    '1min': 1,
    '5min': 5,
    '15min': 15,
    '30min': 30,
    '1h': 60,
    '4h': 240,
    '1D': 1440,
    '1W': 10080,
    '1M': 43200
}

from DataLoader.xAPIConnector import *

def XTB_to_pandas(response):
    data = pd.DataFrame.from_dict(response['returnData']['rateInfos'])
    digits = response['returnData']['digits']

    data['Date'] = data['ctm'].apply(lambda x: dt.fromtimestamp(x/1000))
    data['Price'] = (data['open'] + data['close'])/(10**digits)
    data = data.loc[:, ['Date', 'Price']]
    data = data.set_index('Date')
    data = data.iloc[:, 0]

    return data

class DataLoader:
    def __init__(self, user_id, pwd):
        
        self.user_id = user_id
        self.pwd = pwd
        
        self.client = None
        
    def connect(self, verbose: bool = True):    
        self.client = APIClient()
        if verbose: print(f"[{dt.now()}] Loguję do API...")
        self.client.execute(loginCommand(self.user_id, self.pwd))
    
    def disconnect(self, verbose: bool = True):
        if verbose: print(f"[{dt.now()}] Wylogowuję z API...")
        self.client.disconnect()
        
    def getData(self,
                symbols: list[str],
                start_date: str,
                end_date: str | None = None,
                interval: str = '1min',
                verbose: bool = True):
        
        self.connect(verbose)
        
        finalData = {}
        
        end_date = (dt.strptime(end_date, '%Y-%m-%d %H:%M:%S') if end_date is not None else dt.now())
        endUNIXTIME = int(dt.timestamp(end_date) * 1000)
        start_date = dt.strptime(start_date, '%Y-%m-%d %H:%M:%S') + tmd(days=-1)
        startUNIXTIME = int(dt.timestamp(start_date) * 1000)
        
        for symbol in symbols:
            args = {'info': {
                    'end': endUNIXTIME,
                    'start': startUNIXTIME,
                    'symbol': symbol,
                    'period': period_dict[interval]
            }}
            if verbose: print(f"\tWysyłam zapytanie do API...")
            response = self.client.commandExecute('getChartRangeRequest', arguments=args)
            finalData[symbol] = XTB_to_pandas(response)
        
        self.disconnect(verbose)
        
        return pd.DataFrame(finalData)