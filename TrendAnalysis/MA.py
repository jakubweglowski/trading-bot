import pandas as pd
from TechFunctions.StatisticalFunctions import SMA, EMA
from TechFunctions.Technicalities import position

class MA:
    def __init__(self, 
                 data: pd.DataFrame, 
                 short_window: int = 10, 
                 long_window: int = 22,
                 exponential: bool = True,
                 alpha_EMA: float = 0.1):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.alpha_EMA = alpha_EMA
        
        if exponential:
            self.applyfunction = lambda x: EMA(x, alpha_EMA)
        else:
            self.applyfunction = lambda x: SMA(x)
    
    def Short(self):
        short = self.data.apply(lambda x: x.rolling(self.short_window).apply(self.applyfunction))
        return short
    
    def Long(self):
        long = self.data.apply(lambda x: x.rolling(self.long_window).apply(self.applyfunction))
        return long
    
    def Decision(self):
        UpwardTrend = (self.Short() > self.Long())
        decision = UpwardTrend.apply(lambda col:
            col.rolling(2).apply(lambda x: position(x))
        )
        return decision.fillna(0.0)