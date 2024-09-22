import logging
import os
import pandas

from kraken_bot.Model import Model
from scipy.stats import linregress

class LinearRegression(Model):
    def __init__(self, r_value_target):
        self.r_value_target = r_value_target
        self.log = logging.getLogger(__name__)
        self.log.setLevel(
                getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), logging.INFO)
                )
        self.analysis = pandas.DataFrame({})
        super().__init__(
                interval = 1,
                ascending = False
                )

    def _linear_regression_for_ohlc_data(self, ohlc_data):
        self.log.debug(f"_linear_regression_for_ohlc_data: ohlc_data=...")
        return linregress(ohlc_data['time'].astype(float), ohlc_data['close'].astype(float))

    def _filter_asset_pairs(self, tradable_asset_pairs):
        self.log.debug(f"_filter_asset_pairs: tradable_asset_pairs=...")
        return tradable_asset_pairs[
                (tradable_asset_pairs['quote'] == 'ZUSD') &
                (tradable_asset_pairs['status'] == 'online')
                ]

    def _filter_regressions(self, regressions):
        self.log.debug(f"_filter_regressions: regressions=...")
        regressions.columns = ['slope', 'intercept', 'r_value', 'p_value', 'stderr']
        return regressions[
                (regressions.r_value >= self.r_value_target) &
                (regressions.slope > 0)
                ]

    def _order_regressions(self, regressions):
        self.log.debug(f"_order_regressions: regressions=...")
        return regressions.sort_values(by='slope', ascending=False)

    def since(self):
        return None

    def update(self, tradable_asset_pairs, ohlc_data):
        self.log.debug(f"update: tradable_asset_pairs=..., ohlc_data=...")
        self.analysis = self._order_regressions(
                self._filter_regressions(
                    pandas.DataFrame({
                        asset_pair: self._linear_regression_for_ohlc_data(
                            ohlc_data[asset_pair][0]
                            ) for asset_pair in self._filter_asset_pairs(tradable_asset_pairs).index
                        }).transpose()
                    ))
        self.log.info(f"Completed linear regression analysis of OHLC market data")
        self.log.info(self.analysis)
