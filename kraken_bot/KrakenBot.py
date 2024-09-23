import krakenex
import logging
import os
import scipy
import time

from pykrakenapi import KrakenAPI

class KrakenBot(KrakenAPI):
    def __init__(self, token, secret, tier, model, trading_strategy):
        self.model = model
        self.trading_strategy = trading_strategy
        self.log = logging.getLogger(__name__)
        self.log.setLevel(
                getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), logging.INFO)
                )
        super().__init__(krakenex.API(token, secret), tier=tier)
        self.update(full=True)

    def _delay_factor(self):
        self.log.debug(f"_delay_factor")
        time.sleep(self.factor)
        self.log.debug(f"Delayed {self.factor} seconds")

    def _update_tradable_asset_pairs(self, info=None, pair=None):
        self.log.debug(f"update_tradable_asset_pairs: info={info}, pair={pair}")
        self._delay_factor()
        self.tradable_asset_pairs = self.get_tradable_asset_pairs(info, pair)

    def _filter_tradable_asset_pairs(self):
        self.log.debug(f"_filter_tradable_asset_pairs")
        self.tradable_asset_pairs = self.tradable_asset_pairs[
                (self.tradable_asset_pairs.quote == 'ZUSD') &
                (self.tradable_asset_pairs.status == 'online')
                ]

    def _update_account_balance(self, otp=None):
        self.log.debug(f"_update_account_balance: otp={otp}")
        self._delay_factor()
        self.account_balance = self.get_account_balance(otp)
        self.log.debug(self.account_balance)

    def _filter_account_balance(self):
        self.log.debug(f"_filter_account_balance")
        self.account_balance = self.account_balance[
                (self.account_balance.vol > 0)
                ]
        self.log.debug(self.account_balance)

    def _update_trade_balance(self, aclass='currency', asset='ZUSD', otp=None):
        self.log.debug(f"update_trade_balance: aclass={aclass}, asset={asset}, otp={otp}")
        self._delay_factor()
        self.trade_balance = self.get_trade_balance(aclass, asset, otp)
        self.log.debug(self.trade_balance)

    def _get_ohlc_data(self, pair, interval=1, since=None, ascending=False):
        self.log.debug(f"get_ohlc_data: pair={pair}, interval={interval}, since={since}, ascending={ascending}")
        self._delay_factor()
        return self.get_ohlc_data(pair, interval, since, ascending)

    def _update_ohlc_data(self):
        self.log.debug(f"_update_ohlc_data")
        self.ohlc_data = {
                asset_pair: self._get_ohlc_data(
                    asset_pair, self.model.interval, self.model.since(), self.model.ascending
                    ) for asset_pair in self.tradable_asset_pairs.index
                }

    def _add_standard_order(self, order):
        self.log.debug(f"add_standard_order: order={order}")
        self._delay_factor()
        order = self.add_standard_order(
                order.ordertype, order.type, order.pair, order.userref, order.volume, order.price, order.price2, order.trigger,
                order.leverage, order.oflags, order.timeinforce, order.starttm, order.expiretm, order.close_ordertype,
                order.close_price, order.close_price2, order.deadline, order.validate, order.otp)
        self.log.info(order)
        self.update()

    def update(self, full=False):
        self.log.debug(f"update: full={full}")
        self._update_tradable_asset_pairs()
        self._filter_tradable_asset_pairs()
        self._update_account_balance()
        self._filter_account_balance()
        self._update_trade_balance()
        if full:
            self._update_ohlc_data()
            self.model.update(
                    self.tradable_asset_pairs,
                    self.ohlc_data
                    )
            self.trading_strategy.update(
                    self.tradable_asset_pairs,
                    self.ohlc_data,
                    self.model.analysis,
                    self.account_balance
                    )

    def execute(self):
        self.log.debug(f"execute")
        for order in self.trading_strategy.orders:
            self._add_standard_order(order)
