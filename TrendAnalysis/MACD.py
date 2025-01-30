import pandas as pd
from TechFunctions.StatisticalFunctions import SMA, EMA
from TechFunctions.Technicalities import position

class MACD:
    def __init__(self, 
                 data: pd.DataFrame, 
                 short_window: int = 12, 
                 long_window: int = 26,
                 signal_window: int = 9,
                 exponential: bool = True,
                 alpha_EMA: float = 0.1):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.alpha_EMA = alpha_EMA
        
        if exponential:
            self.applyfunction = lambda x: EMA(x, alpha_EMA)
        else:
            self.applyfunction = lambda x: SMA(x)
     
    def BaseLine(self) -> pd.DataFrame:
        bl = self.data.rolling(self.short_window)\
            .apply(self.applyfunction)\
                - self.data.rolling(self.long_window)\
                    .apply(self.applyfunction)
        return bl
    
    def SignalLine(self) -> pd.DataFrame:
        bl = self.BaseLine()
        sl = bl.rolling(self.signal_window).apply(self.applyfunction)
        return sl

    def Decision(self):
        UpwardTrend = self.BaseLine() > self.SignalLine()
        decision = UpwardTrend.apply(lambda col:
            col.rolling(2).apply(lambda x: position(x)))
        return decision.fillna(0.0)
