import numpy as np
import pandas as pd
from TechFunctions.StatisticalFunctions import SMA, EMA
from Data.SymbolParser import materials

class MeanRevert:
    def __init__(self, 
                 data: pd.DataFrame,
                 window: int = 10,
                 entry: float = 1, 
                 sl: float = 1.5,
                 tp: float = 0.5):
        self.data = data.copy()
        self.symbols = [x for x in self.data.columns if x not in materials]
        self.window = window
        self.entry = entry
        self.sl = sl
        self.tp = tp
    
    def getSignal(self, price_col: str):
        self.data['rolling_mean'] = self.data[price_col].rolling(window=self.window).mean()
        self.data['rolling_std'] = self.data[price_col].rolling(window=self.window).std()
        
        self.data['signal'] = 0

        self.data.loc[(self.data[price_col] > self.data['rolling_mean'] + self.data['rolling_std'] * self.entry) &
                      (self.data[price_col].shift() <= self.data['rolling_mean'].shift() + self.data['rolling_std'].shift() * self.entry), 'signal'] = 1
        self.data.loc[(self.data[price_col] < self.data['rolling_mean'] - self.data['rolling_std'] * self.entry) &
                      (self.data[price_col].shift() >= self.data['rolling_mean'].shift() - self.data['rolling_std'].shift() * self.entry), 'signal'] = -1
        return self.data.loc[:, 'signal']

    def Decision(self):
        decision = pd.DataFrame()
        for col in self.symbols:
            decision.loc[:, col] = self.getSignal(col)
        return decision

    def getBacktest(self, price_col: str):
        if 'signal' not in self.data.columns:
            self.getSignal(price_col)
        
        self.data['position'] = self.data['signal'].shift(1)
        self.data['pnl'] = 0
        self.data['cum_pnl'] = 0
        self.data['comment'] = np.NaN  

        open_position = None
        entry_price = None

        for i in range(1, len(self.data)):
            # print(f"{i}: {open_position}")
            if open_position is None:
                if self.data.loc[self.data.index[i], 'position'] == 1:
                    open_position = 1
                    entry_price = self.data.loc[self.data.index[i], price_col]
                elif self.data.loc[self.data.index[i], 'position'] == -1:  
                    open_position = -1
                    entry_price = self.data.loc[self.data.index[i], price_col]
            else:
                current_price = self.data.loc[self.data.index[i], price_col]
                if open_position == 1:
                    if current_price <= entry_price - self.data.loc[self.data.index[i], 'rolling_std'] * self.sl:  
                        self.data.loc[self.data.index[i], 'pnl'] = current_price - entry_price
                        self.data.loc[self.data.index[i], 'comment'] = 'SL hit'
                        open_position = None
                    elif current_price >= entry_price + self.data.loc[self.data.index[i], 'rolling_std'] * self.tp: 
                        self.data.loc[self.data.index[i], 'pnl'] = current_price - entry_price
                        self.data.loc[self.data.index[i], 'comment'] = 'TP hit'
                        open_position = None
                    else:
                        self.data.loc[self.data.index[i], 'pnl'] = current_price - self.data.loc[self.data.index[i-1], price_col]
                elif open_position == -1:  
                    if current_price >= entry_price + self.data.loc[self.data.index[i], 'rolling_std'] * self.sl:
                        self.data.loc[self.data.index[i], 'pnl'] = entry_price - current_price
                        self.data.loc[self.data.index[i], 'comment'] = 'SL hit'
                        open_position = None
                    elif current_price <= entry_price - self.data.loc[self.data.index[i], 'rolling_std'] * self.tp: 
                        self.data.loc[self.data.index[i], 'pnl'] = entry_price - current_price
                        self.data.loc[self.data.index[i], 'comment'] = 'TP hit'
                        open_position = None
                    else:
                        self.data.loc[self.data.index[i], 'pnl'] = self.data.loc[self.data.index[i-1], price_col] - current_price

        self.data['cum_pnl'] = self.data['pnl'].cumsum()

        return self.data
    
    def saveDecision(self,
                     filename: str):
        self.Decision().to_csv('Data/Signals/'+filename+'.csv', index=False)
