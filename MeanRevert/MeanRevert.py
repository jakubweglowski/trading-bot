import numpy as np
import pandas as pd

def backtest_strategy(data: pd.DataFrame,
                      price_col: str, 
                      sl_col: str,
                      tp_col: str,
                      signal_col: str,
                      size: str):
    trades = []  
    position = None 
    entry_price = None 
    entry_index = None
    entry_size = None
    for i in range(len(data)):
        current_signal = data.loc[data.index[i], signal_col]
        current_price = data.loc[data.index[i], price_col]
        current_size = data.loc[data.index[i], size]

        sl_price = data.loc[data.index[i], sl_col]
        tp_price = data.loc[data.index[i], tp_col]

        if position == 'long':
            if sl_price:
                pnl = entry_size * (current_price - entry_price)
                trades.append({
                    'entry_index': entry_index,
                    'exit_index': data.index[i],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl': pnl,
                    'reason': 'Stop-loss hit'
                })
                position = None
            elif tp_price:
                pnl = entry_size * (current_price - entry_price)
                trades.append({
                    'entry_index': entry_index,
                    'exit_index': data.index[i],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl': pnl,
                    'reason': 'Take-profit hit'
                })
                position = None

        elif position == 'short':
            if sl_price:
                pnl = entry_size * (entry_price - current_price)
                trades.append({
                    'entry_index': entry_index,
                    'exit_index': data.index[i],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl': pnl,
                    'reason': 'Stop-loss hit'
                })
                position = None
            elif tp_price:
                pnl = entry_size * (entry_price - current_price)
                trades.append({
                    'entry_index': entry_index,
                    'exit_index': data.index[i],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl': pnl,
                    'reason': 'Take-profit hit'
                })
                position = None

        if position is None and current_signal != 0:
            position = 'long' if current_signal == 1 else 'short'
            entry_price = current_price
            entry_index = data.index[i]
            entry_size = current_size

    trades_data = pd.DataFrame(trades)
    return trades_data


class MeanRevert:
    def __init__(self, 
                 data: pd.DataFrame,
                 price_col: str,
                 window: int = 10,
                 entry: float = 1, 
                 sl: float = 1.5,
                 tp: float = 0.5):
        self.data = data.copy()
        self.price_col = price_col
        self.window = window
        self.entry = entry
        self.sl = sl
        self.tp = tp
    
    def getSignal(self):
        self.data['rolling_mean'] = self.data[self.price_col].rolling(window=self.window).mean()
        self.data['rolling_std'] = self.data[self.price_col].rolling(window=self.window).std()
        
        self.data['signal'] = 0
        self.data['sl'] = 0
        self.data['tp'] = 0

        self.data.loc[abs(self.data[self.price_col] - self.data['rolling_mean']) < self.data['rolling_std'].shift() * self.tp, 'tp'] = 1
        self.data.loc[abs(self.data[self.price_col] - self.data['rolling_mean']) > self.data['rolling_std'].shift() * self.sl, 'sl'] = 1

        self.data.loc[(self.data[self.price_col] - self.data['rolling_mean'] > self.data['rolling_std'] * self.entry) & 
                      (self.data[self.price_col].shift() - self.data['rolling_mean'].shift() <= self.data['rolling_std'].shift() * self.entry), 'signal'] = -1
        self.data.loc[(self.data[self.price_col] - self.data['rolling_mean'] < -self.data['rolling_std'] * self.entry) & 
                      (self.data[self.price_col].shift() - self.data['rolling_mean'].shift() >= -self.data['rolling_std'].shift() * self.entry), 'signal'] = 1

        self.data['size'] = 1_000 / self.data[self.price_col]

        return self.data
    
    def getBacktest(self):
        backtest_df = backtest_strategy(self.data, self.price_col, 'sl', 'tp', 'signal', 'size')
        return backtest_df



class MeanRevertPairs:
    def __init__(self, 
                 data: pd.DataFrame,
                 price_col: str,
                 price_col2: str,
                 window: int = 10,
                 entry: float = 1, 
                 sl: float = 1.5,
                 tp: float = 0.5):
        self.data = data.copy()
        self.price_col = price_col
        self.price_col2 = price_col2
        self.window = window
        self.entry = entry
        self.sl = sl
        self.tp = tp
    
    def getSignal(self):
        self.data['spread'] = self.data[self.price_col] / self.data[self.price_col2]

        self.data['rolling_mean'] = self.data['spread'].rolling(window=self.window).mean()
        self.data['rolling_std'] = self.data['spread'].rolling(window=self.window).std()
        
        self.data['signal'] = 0
        self.data['sl'] = 0
        self.data['tp'] = 0

        self.data.loc[abs(self.data['spread'] - self.data['rolling_mean']) < self.data['rolling_std'].shift() * self.tp, 'tp'] = 1
        self.data.loc[abs(self.data['spread'] - self.data['rolling_mean']) > self.data['rolling_std'].shift() * self.sl, 'sl'] = 1

        self.data.loc[(self.data['spread'] - self.data['rolling_mean'] > self.data['rolling_std'] * self.entry) & 
                      (self.data['spread'].shift() - self.data['rolling_mean'].shift() <= self.data['rolling_std'].shift() * self.entry), 'signal'] = -1
        self.data.loc[(self.data['spread'] - self.data['rolling_mean'] < -self.data['rolling_std'] * self.entry) & 
                      (self.data['spread'].shift() - self.data['rolling_mean'].shift() >= -self.data['rolling_std'].shift() * self.entry), 'signal'] = 1

        self.data['size'] = 1_000 / self.data[self.price_col] / self.data['spread']
        self.data['size_2'] = 1_000 / self.data[self.price_col]
        return self.data
    
    def getBacktest(self):
        trades = []  
        position = None 
        entry_price = None 
        entry_price_2 = None
        entry_index = None
        entry_size = None
        entry_size_2 = None
        for i in range(len(self.data)):
            current_signal = self.data.loc[self.data.index[i], 'signal']
            sl_price = self.data.loc[self.data.index[i], 'sl']
            tp_price = self.data.loc[self.data.index[i], 'tp']
            current_size = self.data.loc[self.data.index[i], 'size']
            current_size_2 = self.data.loc[self.data.index[i], 'size_2']

            current_price = self.data.loc[self.data.index[i], self.price_col]
            current_price_2 = self.data.loc[self.data.index[i], self.price_col2]


            if position == 'long':
                if sl_price:
                    pnl = entry_size * (current_price - entry_price) - entry_size_2 * (current_price_2 - entry_price_2)
                    trades.append({
                        'entry_index': entry_index,
                        'exit_index': self.data.index[i],
                        'entry_price': entry_price / entry_price_2,
                        'exit_price': current_price / current_price_2,
                        'pnl': pnl,
                        'reason': 'Stop-loss hit'
                    })
                    position = None
                elif tp_price:
                    pnl = entry_size * (current_price - entry_price) - entry_size_2 * (current_price_2 - entry_price_2)
                    trades.append({
                        'entry_index': entry_index,
                        'exit_index': self.data.index[i],
                        'entry_price': entry_price / entry_price_2,
                        'exit_price': current_price / current_price_2,
                        'pnl': pnl,
                        'reason': 'Take-profit hit'
                    })
                    position = None

            elif position == 'short':
                if sl_price:
                    pnl = -entry_size * (current_price - entry_price) + entry_size_2 * (current_price_2 - entry_price_2)
                    trades.append({
                        'entry_index': entry_index,
                        'exit_index': self.data.index[i],
                        'entry_price': entry_price / entry_price_2,
                        'exit_price': current_price / current_price_2,
                        'pnl': pnl,
                        'reason': 'Stop-loss hit'
                    })
                    position = None
                elif tp_price:
                    pnl = -entry_size * (current_price - entry_price) + entry_size_2 * (current_price_2 - entry_price_2)
                    trades.append({
                        'entry_index': entry_index,
                        'exit_index': self.data.index[i],
                        'entry_price': entry_price / entry_price_2,
                        'exit_price': current_price / current_price_2,
                        'pnl': pnl,
                        'reason': 'Take-profit hit'
                    })
                    position = None

            if position is None and current_signal != 0:
                position = 'long' if current_signal == 1 else 'short'
                entry_price = current_price
                entry_price_2 = current_price_2
                entry_index = self.data.index[i]
                entry_size = current_size
                entry_size_2 = current_size_2

        trades_data = pd.DataFrame(trades)
        return trades_data


