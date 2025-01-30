import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from TechFunctions.StatisticalFunctions import EMA
from TechFunctions.Technicalities import position_in_MA_strategy

def cValue(y: pd.Series):
    n = len(y)
    c = np.array(range(1, n+1))
    corr, p = pearsonr(c, np.array(y.values))
    if p > 0.05: corr = 0.0 # korelacja jest pozorna
    return corr

def RSI(y: pd.Series):
    U = y[y>0].sum()
    D = -y[y<0].sum()
    RS = U/D
    rsi = 100-100/(1+RS)
    return rsi

class MACD:
    
    def __init__(self, 
                 y: pd.Series, 
                 short_window: int = 10, 
                 long_window: int = 22,
                 signal_window: int = 9,
                 alpha_EMA: float = 0.1):
        self.y = y
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.alpha_EMA = alpha_EMA
        
        self.decision = None
        
    def BaseLine(self):
        bl = self.y.rolling(self.short_window).apply(lambda x: EMA(x, self.alpha_EMA)) - \
            self.y.rolling(self.long_window).apply(lambda x: EMA(x, self.alpha_EMA))
        return bl
    
    def SignalLine(self):
        bl = self.BaseLine()
        sl = bl.rolling(self.signal_window).apply(lambda x: EMA(x, 0.1))
        return sl

    def UpwardTrendIndicator(self):
        UpwardTrend = self.BaseLine() > self.SignalLine()
        return UpwardTrend
    
    def Decision(self):
        self.decision = self.UpwardTrend.rolling(2).apply(lambda x: position(x))

    