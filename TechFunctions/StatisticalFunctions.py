import pandas as pd
import numpy as np

def EMA(y: pd.Series, alpha: float):
    weights = np.array([(1-alpha)**(len(y)-i+1) for i in range(len(y))])
    return (y.values).dot(weights)/np.sum(weights)