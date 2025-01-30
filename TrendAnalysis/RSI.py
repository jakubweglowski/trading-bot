import pandas as pd
from TechFunctions.TrendMeasures import rsi

def clean_rsi_decision(x: pd.Series):
    if x.iloc[0] == x.iloc[1]: return 0
    else: return x.iloc[1]
    
class RSI:
    def __init__(self, 
                 data: pd.DataFrame,
                 window: int = 26):
        self.data = data
        self.window = window
        
    def compute_index(self):
        RSIndex = self.data.apply(lambda col:
            col.diff().rolling(self.window).apply(lambda x: rsi(x))
        )
        return RSIndex
    
    def Decision(self):
        RSIndex = self.compute_index()
        
        SellSignal = (RSIndex >= 70)*(-1.0)
        BuySignal = (RSIndex <= 30)*(1.0)
        WaitSignal = ((RSIndex > 30) & (RSIndex < 70))*(1.0)
        
        decision = SellSignal + WaitSignal + BuySignal
        decision = decision.rolling(2).apply(clean_rsi_decision)
        return decision.fillna(0.0)