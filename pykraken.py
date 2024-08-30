import base64
import hashlib
import hmac
import os
import requests
import time
import urllib.parse

class Kraken():

    class Order():

        class Close():
            def __init__(self, ordertype, price, price2):
                self.ordertype = ordertype
                self.price = price
                self.price2 = price2

            def asdict(self):
                data = {
                        'ordertype': self.ordertype,
                        'price': self.price
                        }
                if self.price2:
                    data['price2'] = self.price2
                return data

        def __init__(self, ordertype, price, type, volume, close=None, pair=None, price2=None, timeinforce=None, userref=None):
            self.close = close
            self.ordertype = ordertype
            self.pair = pair
            self.price = price
            self.price2 = price2
            self.timeinforce = timeinforce
            self.type = type
            self.userref = userref
            self.volume = volume

        def asdict(self):
            data = {
                    'nonce': str(int(1000*time.time())),
                    'ordertype': self.ordertype,
                    'price': self.price,
                    'type': self.type,
                    'volume': self.volume
                    }
            if self.close:
                data['close'] = self.close
            if self.pair:
                data['pair'] = self.pair
            if self.price2:
                data['price2'] = self.price2
            if self.timeinforce:
                data['timeinforce'] = self.timeinforce
            if self.userref:
                data['userref'] = self.userref
            return data

    class KrakenError(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return f'Kraken API Error: {self.message}'

    # Core
    def __init__(self):
        self.api_url = 'https://api.kraken.com/'
        self.api_token = os.getenv('KRAKEN_API_TOKEN')
        self.api_sec = os.getenv('KRAKEN_API_SEC')
        self.asset_pairs = self.get_asset_pairs()['result']

    def _kraken_signature(self, urlpath, data, secret):
        return base64.b64encode(
                hmac.new(
                    base64.b64decode(secret),
                    urlpath.encode() + hashlib.sha256(
                        (str(data['nonce']) + urllib.parse.urlencode(data)).encode()
                        ).digest(),
                    hashlib.sha512
                    ).digest()).decode()

    def _kraken_post(self, uri_path, data):
        resp = requests.post(
                f'{self.api_url}{uri_path}',
                headers = {
                    'API-Key': self.api_sec,
                    'API-Sign': self._kraken_signature(uri_path, data, self.api_sec)
                    },
                data=data
                ).json()
        for error in resp['error']:
            raise self.KrakenError(error)

    def _kraken_get(self, uri_path):
        resp = requests.get(f'{self.api_url}{uri_path}').json()
        for error in resp['error']:
            raise self.KrakenError(err)
        return resp

    # Misc.
    def get_asset_markets(self, asset):
        return [
                each for each in self.asset_pairs if
                self.asset_pairs[each]['base'] == asset or 
                self.asset_pairs[each]['quote'] == asset
                ]

    # Spot market data
    def get_asset_pairs(self):
        return _kraken_get('/0/public/AssetPairs')

    def get_ohlc(self, asset_pair):
        return _kraken_get('/0/public/OHLC?pair={asset_pair}')

    def get_depth(self, asset_pair):
        return _kraken_get('/0/public/Depth?pair={asset_pair}')

    def get_trades(self, asset_pair):
        return _kraken_get('/0/public/Trades?pair={asset_pair}')

    def get_spread(self, asset_pair):
        return _kraken_get('/0/public/Spread?pair={asset_pair}')

    # Account data
    def get_account_balance(self):
        return self._kraken_post('/0/private/Balance', {'nonce': str(int(1000*time.time()))})

    # Spot trading
    def add_order(self, order):
        return self._kraken_post('/0/private/AddOrder', dict(order))
