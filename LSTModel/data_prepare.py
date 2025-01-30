import pandas as pd
import numpy as np
from datetime import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from copy import deepcopy as dc


def prepare_data_for_LSTM_training(data: pd.Series, window: int, skip: int,split : float) -> tuple:   
    # można ustawić okna zachodzące (0 < skip < window)
    # można ustawić niezachodzące (skip >= window)
    assert skip > 0, "Pętla w kodzie nigdy się nie zakończy..."
    
    # Generujemy 'okna'
    X = pd.DataFrame(columns=range(window+1))
    
    i = len(data)
    count = 0
    while i >= window+1:
        temp_y = data.iloc[i-window-1:i]
        
        X.loc[count, :] = temp_y.values
        
        i = i - skip    
        count += 1
        
    X=np.array(X)
    
    
    scaler = MinMaxScaler(feature_range=(-1, 1))
    X = scaler.fit_transform(X)
    
    x=X[:,1:]
    y=X[:,0]
    
    
    x=dc(np.flip(x, axis=1))
    
    split_index=int(len(y) * split)
    
    X_train = x[:split_index]
    X_test = x[split_index:]
    y_train = y[:split_index]
    y_test = y[split_index:]
    
    
    X_train = X_train.reshape((-1, window, 1))
    X_test = X_test.reshape((-1, window, 1))
    y_train = y_train.reshape((-1, 1))
    y_test = y_test.reshape((-1, 1))
    
    
    X_train = torch.tensor(X_train).float()
    y_train = torch.tensor(y_train).float()
    X_test = torch.tensor(X_test).float()
    y_test = torch.tensor(y_test).float()
    
    return X_train,y_train,X_test,y_test,scaler



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