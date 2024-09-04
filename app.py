import krakenex
import os
import pandas

from dotenv import load_dotenv
from pykrakenapi import KrakenAPI
from scipy.stats import linregress
from time import sleep

k = krakenex.API()
k.load_key('kraken.key')
kraken = KrakenAPI(k, tier='Pro')

def filter_asset_pairs(tradable_asset_pairs):
    return tradable_asset_pairs[
            (tradable_asset_pairs['quote'] == 'ZUSD') &
            (tradable_asset_pairs['status'] == 'online')
            ]

def model_asset_pair(asset_pair):
    sleep(1)
    ohlc = kraken.get_ohlc_data(asset_pair)[0]
    model = pandas.DataFrame({
        'open': linregress(ohlc['time'].astype(float), ohlc['open'].astype(float)),
        'high': linregress(ohlc['time'].astype(float), ohlc['high'].astype(float)),
        'low': linregress(ohlc['time'].astype(float), ohlc['low'].astype(float)),
        'close': linregress(ohlc['time'].astype(float), ohlc['close'].astype(float))
        }).transpose()
    model.columns = ['slope', 'intercept', 'r_value', 'p_value', 'stderr']
    return model

def grade_models(models):
    model_averages = pandas.DataFrame({
            model: {
                'slope': models[model].slope.mean(),
                'intercept': models[model].intercept.mean(),
                'r_value': models[model].r_value.mean(),
                'p_value': models[model].p_value.mean(),
                'stderr': models[model].stderr.mean()
                } for model in models
            }).transpose()
    filtered_models = model_averages[model_averages['r_value'] >= os.getenv('R_VALUE_TARGET')]
    return filtered_models.sort_values(by='slope', ascending=False)

def sell_asset(market, volume):
    kraken.add_standard_order(
            ordertype = 'market',
            type = 'sell',
            pair = market,
            volume = volume
            )

def buy_asset(market, volume):
    kraken.add_standard_order(
            ordertype = 'market',
            type = 'buy',
            pair = market,
            volume = volume
            )

if __name__ == '__main__':
    load_dotenv()

    asset_pairs = filter_asset_pairs(kraken.get_tradable_asset_pairs())
    graded_models = grade_models(
            {asset_pair: model_asset_pair(asset_pair) for asset_pair in asset_pairs.index}
            )

    account_balance = kraken.get_account_balance()
    for asset in account_balance.index.drop('ZUSD'):
        market = asset_pairs[asset_pairs['base'] == asset]
        if market.index[0] not in graded_models[:5].index:
            sell_asset(market, account_balance.loc[asset].vol)

    while len(account_balance := kraken.get_account_balance()) - 1 < os.getenv('INVESTMENT_COUNT'): 
        if account_balance.loc['ZUSD'] <= os.getenv('INVESTMENT_VOLUME'):
            break
        for market in graded_models:
            if asset_pairs.loc[market].base not in account_balance.index:
                buy_asset(market, os.getenv('INVESTMENT_VOLUME'))
                break
