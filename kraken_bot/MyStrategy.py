from kraken_bot.TradingStrategy import TradingStrategy
from kraken_bot.KrakenOrder import KrakenOrder

class MyStrategy(TradingStrategy):
    def __init__(self, investment_count, investment_volume):
        super().__init__(investment_count, investment_volume)

    def update(self, tradable_asset_pairs, ohlc_data, market_analysis, account_balance):
        self.orders = []
        investment_count = len(account_balance) - 1
        for asset in account_balance[(account_balance.index != 'ZUSD')].index:
            market = tradable_asset_pairs[
                    (tradable_asset_pairs.base == asset) &
                    (tradable_asset_pairs.quote == 'ZUSD')
                    ].iloc[0]
            if market.altname not in market_analysis.index:
                self.orders.append(KrakenOrder(
                    ordertype = 'market',
                    type = 'sell',
                    pair = market.altname,
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
