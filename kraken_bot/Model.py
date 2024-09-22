from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, interval, ascending):
        self.interval = interval
        self.ascending = ascending

    @abstractmethod
    def since():
        pass

    @abstractmethod
    def update(self, tradable_asset_pairs, ohlc_data, account_balance, trade_balance):
        pass
