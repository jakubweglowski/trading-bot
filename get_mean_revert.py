import numpy as np
import pandas as pd

from DataLoader.xAPIConnector import *
from DataLoader.DataLoader import *
from DataLoader.config import user_id, pwd
from Data.SymbolParser import parse_symbols
from MeanRevert.MeanRevert import MeanRevert, MeanRevertPairs

SYMBOLS = parse_symbols()

for commodity in SYMBOLS.keys():
    symbols = SYMBOLS[commodity]
    start, interval = '2010-01-01', '1D'

    dl = DataLoader(user_id, pwd)
    data = dl.getData(symbols=symbols, start_date=start, interval=interval, verbose=False)
    data = data.dropna()

    for col in data.columns[:-4]:
        mean_revert = MeanRevert(data, col)
        mean_revert.getSignal()
        backtest_df = mean_revert.getBacktest()
        backtest_df.to_csv(f'App/data/{commodity.capitalize()}/{col[:-3].lower()}_mean_revert.csv')

        mean_revert = MeanRevertPairs(data, col, commodity.upper())
        mean_revert.getSignal()
        backtest_df = mean_revert.getBacktest()
        backtest_df.to_csv(f'App/data/{commodity.capitalize()}/{col[:-3].lower()}_vs_silver_mean_revert.csv')
