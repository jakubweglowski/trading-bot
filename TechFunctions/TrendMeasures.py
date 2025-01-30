import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def cvalue(y: pd.Series):
    n = len(y)
    c = np.array(range(1, n+1))
    corr, p = pearsonr(c, np.array(y.values))
    if p > 0.05: corr = 0.0 # korelacja jest pozorna
    return corr

def rsi(y: pd.Series):
    U = y[y>0].sum()
    D = y[y<0].sum()
    RS = -U/D
    rsi_ = 100-100/(1+RS)
    return rsi_
    