import pandas as pd
from TechFunctions.TrendMeasures import rsi

def clean_rsi_decision(x: pd.Series):
    if x.iloc[0] == x.iloc[1]: return 0
    else: return x.iloc[1]
    
class RSI:
    def __init__(self, 
                 data: pd.DataFrame,
                 window: int = 26,
                 sell_signal: float = 70.0,
                 buy_signal: float = 30.0):
        self.data = data
        self.window = window
        self.sell_signal = sell_signal
        self.buy_signal = buy_signal
        
    def compute_index(self):
        RSIndex = self.data.apply(lambda col:
            col.diff().rolling(self.window).apply(lambda x: rsi(x))
        )
        return RSIndex
    
    def Decision(self):
        RSIndex = self.compute_index()
        
        SellSignal = (RSIndex >= self.sell_signal)*(-1.0)
        BuySignal = (RSIndex <= self.sell_signal)*(1.0)
        WaitSignal = ((RSIndex > self.buy_signal) & (RSIndex < self.sell_signal))*(1.0)
        
        decision = SellSignal + WaitSignal + BuySignal
        decision = decision.rolling(2).apply(clean_rsi_decision)
        return decision.fillna(0.0)