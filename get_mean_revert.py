import numpy as np
import pandas as pd

from DataLoader.xAPIConnector import *
from DataLoader.DataLoader import *
from DataLoader.config import user_id, pwd
from Data.SymbolParser import parse_symbols
from MeanRevert.MeanRevert import MeanRevert, MeanRevertPairs

SYMBOLS = parse_symbols()

results = pd.DataFrame(columns=['company', 'commodity', 'strategy', 'mean_std', 'win_rate'])
i = 0
for commodity in SYMBOLS.keys():
    symbols = SYMBOLS[commodity]
    start, interval = '2010-01-01', '1D'

    dl = DataLoader(user_id, pwd)
    data = dl.getData(symbols=symbols, start_date=start, interval=interval, verbose=False)
    data = data.dropna()

    commodity_price = data[[commodity.upper()]]
    commodity_price.columns = ['Price']
    commodity_price.index.name = 'Date'
    commodity_price.to_csv(f'App/data/{commodity.capitalize()}/spot_price.csv')

    for col in data.columns[:-4]:
        mean_revert = MeanRevert(data, col)
        mean_revert.getSignal()
        backtest_df = mean_revert.getBacktest()
        backtest_df.to_csv(f'App/data/{commodity.capitalize()}/{col[:-3].lower()}_mean_revert.csv', index=False)

        results.loc[i] = [col, commodity, 'base', backtest_df.pnl.mean() / backtest_df.pnl.std(), (backtest_df.pnl.mean()>0).mean()]
        i += 1

        mean_revert = MeanRevertPairs(data, col, commodity.upper())
        mean_revert.getSignal()
        backtest_df = mean_revert.getBacktest()
        backtest_df.to_csv(f'App/data/{commodity.capitalize()}/{col[:-3].lower()}_vs_{commodity.lower()}_mean_revert.csv', index=False)

        results.loc[i] = [col, commodity, 'vs', backtest_df.pnl.mean() / backtest_df.pnl.std(), (backtest_df.pnl>0).mean()]
        i += 1
        

results.to_csv('results.csv')