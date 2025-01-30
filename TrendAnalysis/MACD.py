import pandas as pd
from TechFunctions.StatisticalFunctions import EMA
from TechFunctions.Technicalities import position

class MACD:
    
    def __init__(self, 
                 data: pd.DataFrame, 
                 short_window: int = 10, 
                 long_window: int = 22,
                 signal_window: int = 9,
                 alpha_EMA: float = 0.1):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.alpha_EMA = alpha_EMA
     
    def BaseLine(self) -> pd.DataFrame:
        bl = self.data.rolling(self.short_window)\
            .apply(lambda x: EMA(x, self.alpha_EMA))\
                - self.data.rolling(self.long_window)\
                    .apply(lambda x: EMA(x, self.alpha_EMA))
        return bl
    
    def SignalLine(self) -> pd.DataFrame:
        bl = self.BaseLine()
        sl = bl.rolling(self.signal_window).apply(lambda x: EMA(x, 0.1))
        return sl

    def Decision(self):
        decision = pd.DataFrame()
        UpwardTrend = self.BaseLine() > self.SignalLine()
        for symbol in UpwardTrend.columns:
            y = UpwardTrend.loc[:, symbol]
            decision.loc[:, symbol] = y.rolling(2).apply(lambda x: position(x))
        return decision
