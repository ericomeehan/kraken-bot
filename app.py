import krakenex
import pandas

from dotenv import load_dotenv
from pykrakenapi import KrakenAPI
from scipy.stats import linregress
from time import sleep

k = krakenex.API()
k.load_key('kraken.key')
kraken = KrakenAPI(k, tier='Pro')

def get_markets_by_asset(asset):
    tradable_asset_pairs = kraken.get_tradable_asset_pairs()
    return tradable_asset_pairs[
            ((tradable_asset_pairs['base'] == asset | tradable_asset_pairs['quote'] == asset)
                & (tradable_asset_pairs['status'] == 'online'))
            ]

def get_ohlc_linear_regression(ohlc):
    regressions = pandas.DataFrame({
        'open': linregress(ohlc['time'].astype(float), ohlc['open'].astype(float)),
        'high': linregress(ohlc['time'].astype(float), ohlc['high'].astype(float)),
        'low': linregress(ohlc['time'].astype(float), ohlc['low'].astype(float)),
        'close': linregress(ohlc['time'].astype(float), ohlc['close'].astype(float))
        }).transpose()
    regressions.columns = ['slope', 'intercept', 'r_value', 'p_value', 'stderr']
    return regressions
