import krakenex
import pandas
import time

from pykrakenapi import KrakenAPI
from scipy.stats import linregress

class KrakenBot():
    def __init__(self, kraken_api_token, kraken_api_sec, tier, r_value_target, investment_count, investment_volume):
        self.r_value_target = r_value_target
        self.investment_count = investment_count
        self.investment_volume = investment_volume
        k = krakenex.API(kraken_api_token, kraken_api_sec)
        self.kraken = KrakenAPI(k, tier=tier)

    def filter_asset_pairs(self, tradable_asset_pairs):
        return tradable_asset_pairs[
                (tradable_asset_pairs['quote'] == 'ZUSD') &
                (tradable_asset_pairs['status'] == 'online')
                ]

    def model_asset_pair(self, asset_pair):
        ohlc = self.kraken.get_ohlc_data(asset_pair)[0]
        time.sleep(self.kraken.factor)
        model = pandas.DataFrame({
            'open': linregress(ohlc['time'].astype(float), ohlc['open'].astype(float)),
            'high': linregress(ohlc['time'].astype(float), ohlc['high'].astype(float)),
            'low': linregress(ohlc['time'].astype(float), ohlc['low'].astype(float)),
            'close': linregress(ohlc['time'].astype(float), ohlc['close'].astype(float))
            }).transpose()
        model.columns = ['slope', 'intercept', 'r_value', 'p_value', 'stderr']
        return model

    def grade_models(self, models):
        model_averages = pandas.DataFrame({
                model: {
                    'slope': models[model].slope.mean(),
                    'intercept': models[model].intercept.mean(),
                    'r_value': models[model].r_value.mean(),
                    'p_value': models[model].p_value.mean(),
                    'stderr': models[model].stderr.mean()
                    } for model in models
                }).transpose()
        filtered_models = model_averages[
                (model_averages['r_value'] >= self.r_value_target) &
                (model_averages['slope'] > 0)
                ]
        return filtered_models.sort_values(by='slope', ascending=False)

    def sell_asset(self, market, volume):
        self.kraken.add_standard_order(
                ordertype = 'market',
                type = 'sell',
                pair = market,
                volume = volume,
                validate = False
                )
        time.sleep(self.kraken.factor)
        print(f"Sold {volume} on {market}")

    def buy_asset(self, market, volume):
        self.kraken.add_standard_order(
                ordertype = 'market',
                type = 'buy',
                pair = market,
                volume = volume,
                validate = False
                )
        print(f"Purchased {volume} on {market}")
        time.sleep(self.kraken.factor)

    def update(self):
        asset_pairs = self.filter_asset_pairs(self.kraken.get_tradable_asset_pairs())
        time.sleep(self.kraken.factor)
        graded_models = self.grade_models(
                {asset_pair: self.model_asset_pair(asset_pair) for asset_pair in asset_pairs.index}
                )
        print(graded_models)

        account_balance = self.kraken.get_account_balance()
        for asset in account_balance.index:
            if asset != 'ZUSD':
                market = graded_models[
                        (graded_models.base == asset) &
                        (graded_models.quote == 'ZUSD')
                        ]
                if market.index[0] not in graded_models[:self.investment_count].index:
                    self.sell_asset(market, account_balance.loc[asset].vol)

        account_balance = self.kraken.get_account_balance()
        while ((len(account_balance[account_balance.vol > 0]) - 1 < self.investment_count) &
                (account_balance.loc['ZUSD'].vol > self.investment_volume)):
            for market in graded_models.index:
                if asset_pairs.loc[market].base not in account_balance[account_balance.vol > 0].index:
                    ohlc, last = self.kraken.get_ohlc_data(market)
                    volume = self.investment_volume/ohlc.iloc[-1].close
                    self.buy_asset(market, volume)
                    account_balance = self.kraken.get_account_balance()
                    time.sleep(self.kraken.factor)
                    break

        print(self.kraken.get_account_balance())
        print(self.kraken.get_trade_balance(asset='ZUSD'))
