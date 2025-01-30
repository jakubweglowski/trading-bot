import numpy as np
import pandas as pd

class Mean_Revert:
    def __init__(self, 
                 data: pd.DataFrame,
                 roll: int = 10,
                 entry: float = 1, 
                 sl: float = 1.5,
                 tp: float = 0.5):
        self.data = data.copy()
        self.roll = roll
        self.entry = entry
        self.sl = sl
        self.tp = tp
    
    def get_signal(self, price_col: str):
        """
        Generates trading signals based on mean reversion strategy.
        """
        self.data['rolling_mean'] = self.data[price_col].rolling(window=self.roll).mean()
        self.data['rolling_std'] = self.data[price_col].rolling(window=self.roll).std()
        
        self.data['signal'] = 0

        self.data.loc[(self.data[price_col] > self.data['rolling_mean'] + self.data['rolling_std'] * self.entry) &
                      (self.data[price_col].shift() <= self.data['rolling_mean'].shift() + self.data['rolling_std'].shift() * self.entry), 'signal'] = -1
        self.data.loc[(self.data[price_col] < self.data['rolling_mean'] - self.data['rolling_std'] * self.entry) &
                      (self.data[price_col].shift() >= self.data['rolling_mean'].shift() - self.data['rolling_std'].shift() * self.entry), 'signal'] = -1


    def get_backtest(self, price_col: str):
        if 'signal' not in self.data.columns:
            self.get_signal(price_col)
        
        self.data['position'] = self.data['signal'].shift(1)
        self.data['pnl'] = 0
        self.data['cum_pnl'] = 0
        self.data['comment'] = np.NaN  

        open_position = None
        entry_price = None

        for i in range(1, len(self.data)):
            if open_position is None:
                if self.data.loc[i, 'position'] == 1:
                    open_position = 1
                    entry_price = self.data.loc[i, price_col]
                elif self.data.loc[i, 'position'] == -1:  
                    open_position = -1
                    entry_price = self.data.loc[i, price_col]
            else:
                current_price = self.data.loc[i, price_col]
                if open_position == 1:
                    if current_price <= entry_price - self.data.loc[i, 'rolling_std'] * self.sl:  
                        self.data.loc[i, 'pnl'] = current_price - entry_price
                        self.data.loc[i, 'comment'] = 'SL hit'
                        open_position = None
                    elif current_price >= entry_price + self.data.loc[i, 'rolling_std'] * self.tp: 
                        self.data.loc[i, 'pnl'] = current_price - entry_price
                        self.data.loc[i, 'comment'] = 'TP hit'
                        open_position = None
                    else:
                        self.data.loc[i, 'pnl'] = current_price - self.data.loc[i-1, price_col]
                elif open_position == -1:  
                    if current_price >= entry_price + self.data.loc[i, 'rolling_std'] * self.sl:
                        self.data.loc[i, 'pnl'] = entry_price - current_price
                        self.data.loc[i, 'comment'] = 'SL hit'
                        open_position = None
                    elif current_price <= entry_price - self.data.loc[i, 'rolling_std'] * self.tp: 
                        self.data.loc[i, 'pnl'] = entry_price - current_price
                        self.data.loc[i, 'comment'] = 'TP hit'
                        open_position = None
                    else:
                        self.data.loc[i, 'pnl'] = self.data.loc[i-1, price_col] - current_price

        self.data['cum_pnl'] = self.data['pnl'].cumsum()

        return self.data
