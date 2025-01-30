import pandas as pd
from datetime import datetime as dt, timedelta as tmd
from TechFunctions.Technicalities import XTB_to_pandas, period_dict
from Data.SymbolParser import materials

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
                interval: str = '1D',
                verbose: bool = True):
        
        finalData = {}
        
        end_date = (dt.strptime(end_date, '%Y-%m-%d 00:00:00') if end_date is not None else dt.now())
        endUNIXTIME = int(dt.timestamp(end_date) * 1000)
        start_date = dt.strptime(start_date, '%Y-%m-%d 00:00:00') + tmd(days=-1)
        startUNIXTIME = int(dt.timestamp(start_date) * 1000)
        
        symbols.extend(materials)
        for symbol in symbols:
            
            self.connect(verbose)
            
            try:
                args = {'info': {
                        'end': endUNIXTIME,
                        'start': startUNIXTIME,
                        'symbol': symbol,
                        'period': period_dict[interval]
                }}
                if verbose: print(f"\tWysyłam zapytanie do API...")
                response = self.client.commandExecute('getChartRangeRequest', arguments=args)
                finalData[symbol] = XTB_to_pandas(response)
            except:
                try:
                    args = {'info': {
                            'end': endUNIXTIME,
                            'start': startUNIXTIME,
                            'symbol': symbol+'_4',
                            'period': period_dict[interval]
                    }}
                    if verbose: print(f"\tWysyłam zapytanie do API...")
                    response = self.client.commandExecute('getChartRangeRequest', arguments=args)
                    finalData[symbol] = XTB_to_pandas(response)
                except:
                    print(f"[BŁĄD] Nie pobrano {symbol}")
                    continue
        
            self.disconnect(verbose)
        
        return pd.DataFrame(finalData)