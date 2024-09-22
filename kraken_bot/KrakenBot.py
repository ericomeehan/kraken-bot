import krakenex
import logging
import os
import scipy
import time

from pykrakenapi import KrakenAPI

class KrakenBot(KrakenAPI):
    class KrakenOrder():
        def __init__(self, ordertype, type, pair, userref=None, volume=None, price=None, price2=None, trigger=None, leverage=None,
                oflags=None, timeinforce=None, starttm=0, expiretm=0, close_ordertype=None, close_price=None, close_price2=None,
                deadline=None, validate=True, otp=None):
            self.ordertype = ordertype
            self.type = type
            self.pair = pair
            self.userref = userref
            self.volume = volume
            self.price = price
            self.price2 = price2
            self.trigger = trigger
            self.leverage = leverage
            self.oflags = oflags
            self.timeinforce = timeinforce
            self.starttm = starttm
            self.expiretm = expiretm
            self.close_ordertype = close_ordertype
            self.close_price = close_price
            self.close_price2 = close_price2
            self.deadline = deadline
            self.validate = validate
            self.otp = otp

        def __str__(self):
            return str({
                'ordertype': self.ordertype,
                'type': self.type,
                'pair': self.pair,
                'userref': self.userref,
                'volume': self.volume,
                'price': self.price,
                'price2': self.price2,
                'trigger': self.trigger,
                'leverage': self.leverage,
                'oflags': self.oflags,
                'timeinforce': self.timeinforce,
                'starttm': self.starttm,
                'expiretm': self.expiretm,
                'close_ordertype': self.close_ordertype,
                'close_price': self.close_price,
                'close_price2': self.close_price2,
                'deadline': self.deadline,
                'validate': self.validate,
                'otp': self.otp
                })

    def __init__(self, token, secret, tier, investment_count, investment_volume):
        self.investment_count = investment_count
        self.investment_volume = investment_volume
        self.log = logging.getLogger(__name__)
        self.log.setLevel(
                getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), logging.INFO)
                )
        super().__init__(krakenex.API(token, secret), tier=tier)
        self.update()

    def _delay_factor(self):
        self.log.debug(f"_delay_factor")
        time.sleep(self.factor)
        self.log.debug(f"Delayed {self.factor} seconds")

    def _update_tradable_asset_pairs(self, info=None, pair=None):
        self.log.debug(f"update_tradable_asset_pairs: info={info}, pair={pair}")
        self._delay_factor()
        self.tradable_asset_pairs = self.get_tradable_asset_pairs(info, pair)

    def _update_account_balance(self, otp=None):
        self.log.debug(f"update_account_balance: otp={otp}")
        self._delay_factor()
        self.account_balance = self.get_account_balance(otp)
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

    def _add_standard_order(self, order):
        self.log.debug(f"add_standard_order: order={order}")
        self._delay_factor()
        order = self.add_standard_order(
                order.ordertype, order.type, order.pair, order.userref, order.volume, order.price, order.price2, order.trigger,
                order.leverage, order.oflags, order.timeinforce, order.starttm, order.expiretm, order.close_ordertype,
                order.close_price, order.close_price2, order.deadline, order.validate, order.otp)
        self.log.info(order)
        self.update()

    def update(self):
        self.log.debug(f"update")
        self._update_tradable_asset_pairs()
        self._update_account_balance()
        self._update_trade_balance()

    def trade(self, model):
        self.log.debug(f"trade")
        model.update(
                self.tradable_asset_pairs,
                {
                    asset_pair: self._get_ohlc_data(
                        asset_pair, model.interval, model.since(), model.ascending
                        ) for asset_pair in self.tradable_asset_pairs.index
                    }
                )
        for asset in self.account_balance[(self.account_balance.index != 'ZUSD') & (self.account_balance.vol > 0)].index:
            market = self.tradable_asset_pairs[
                    (self.tradable_asset_pairs.base == asset) &
                    (self.tradable_asset_pairs.quote == 'ZUSD')
                    ].iloc[0]
            if market.altname not in model.analysis.index:
                self._add_standard_order(self.KrakenOrder(
                    ordertype = 'market',
                    type = 'sell',
                    pair = market.altname,
                    volume = self.account_balance.loc[asset].vol,
                    validate = False
                    ))
        while ((len(self.account_balance[self.account_balance.vol > 0]) - 1 < self.investment_count) &
                (self.account_balance.loc['ZUSD'].vol > self.investment_volume)):
            for market in model.analysis.index:
                if self.tradable_asset_pairs.loc[market].base not in self.account_balance[self.account_balance.vol > 0].index:
                    ohlc, last = self._get_ohlc_data(market)
                    volume = self.investment_volume / ohlc.iloc[-1].close
                    self._add_standard_order(self.KrakenOrder(
                        ordertype = 'market',
                        type = 'buy',
                        pair = market,
                        volume = volume,
                        validate = False
                        ))
                    break
