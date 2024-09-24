from kraken_bot.TradingStrategy import TradingStrategy
from kraken_bot.KrakenOrder import KrakenOrder

class HighLowCutoff(TradingStrategy):
    def __init__(self, investment_count, investment_volume, target_gain, max_loss):
        super().__init__(investment_count, investment_volume)
        self.target_gain = self.investment_volume * (1 + target_gain)
        self.max_loss = self.investment_volume * (1 - max_loss)

    def update(self, tradable_asset_pairs, ohlc_data, market_analysis, account_balance):
        self.orders = []
        investment_count = len(account_balance) - 1
        for asset in account_balance[(account_balance.index != 'ZUSD')].index:
            market = tradable_asset_pairs[
                    (tradable_asset_pairs.base == asset) &
                    (tradable_asset_pairs.quote == 'ZUSD')
                    ]
            ohlc, last = ohlc_data[market.index[0]]
            last_close = ohlc.iloc[-1].close
            value = account_balance.loc[asset].vol * last_close
            if (value <= self.max_loss) or (value >= self.target_gain):
                self.orders.append(KrakenOrder(
                    ordertype = 'market',
                    type = 'sell',
                    pair = market.index[0],
                    volume = account_balance.loc[asset].vol,
                    validate = False
                    ))
                investment_count -= 1
        new_investments = []
        while investment_count < self.investment_count:
            for market in market_analysis.index:
                base = tradable_asset_pairs.loc[market].base
                if base not in account_balance.index and base not in new_investments:
                    ohlc, last = ohlc_data[market]
                    volume = self.investment_volume / ohlc.iloc[-2].close
                    self.orders.append(KrakenOrder(
                        ordertype = 'market',
                        type = 'buy',
                        pair = market,
                        volume = volume,
                        validate = False
                        ))
                    new_investments.append(base)
                    investment_count += 1
                    break
