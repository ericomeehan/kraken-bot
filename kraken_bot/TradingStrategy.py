from abc import ABC, abstractmethod
from kraken_bot.KrakenOrder import KrakenOrder

class TradingStrategy(ABC):
    def __init__(self, investment_count, investment_volume):
        self.investment_count = investment_count
        self.investment_volume = investment_volume
        self.orders = []

    @abstractmethod
    def update(self, tradable_asset_pairs, ohlc_data, market_analysis, account_balance):
        pass
