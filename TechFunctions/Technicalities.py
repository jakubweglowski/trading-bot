import pandas as pd
import numpy as np
from datetime import datetime as dt

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

position_encoding ={
    0: 'hold',
    1: 'buy',
    -1: 'sell'
}

def XTB_to_pandas(response):
    data = pd.DataFrame.from_dict(response['returnData']['rateInfos'])
    digits = response['returnData']['digits']

    data['Date'] = data['ctm'].apply(lambda x: dt.fromtimestamp(x/1000))
    data['Price'] = (data['open'] + data['close'])/(10**digits)
    data = data.loc[:, ['Date', 'Price']]
    data = data.set_index('Date')
    data = data.iloc[:, 0]

    return data

def position(x: pd.Series):
    if x.iloc[0] == True and x.iloc[1] == False: return -1
    elif x.iloc[0] == False and x.iloc[1] == True: return 1
    else: return 0
    
def prepare_data_for_LSTM(data: pd.Series, window: int, skip: int) -> tuple:   
    # można ustawić okna zachodzące (0 < skip < window)
    # można ustawić niezachodzące (skip >= window)
    assert skip > 0, "Pętla w kodzie nigdy się nie zakończy..."
    
    # Generujemy 'okna'
    X = pd.DataFrame(columns=range(window))
    
    i = len(data)
    count = 0
    while i >= window:
        temp_y = data.iloc[i-window:i]
        
        X.loc[count, :] = temp_y.values
        
        i = i - skip    
        count += 1
        
    return np.array(X)
