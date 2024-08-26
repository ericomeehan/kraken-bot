import base64
import hashlib
import hmac
import os
import requests
import time
import urllib.parse

class Kraken():
    ASSETS = [
            'ZUSD',
            'XETH',
            'XXBT'
            ]

    ASSET_PAIRS = {
            'ZUSD': {
                'ETHUSD': 'XETHZUSD',
                'XBTUSD': 'XXBTZUSD'
                },
            'XETH': {
                'ETHUSD': 'XETHZUSD',
                'ETHXBT': 'XETHXXBT'
                },
            'XXBT': {
                'ETHXBT': 'XETHXXBT',
                'XBTUSD': 'XXBTZUSD'
                }
            }

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

    def __init__(self):
        self.api_url = 'https://api.kraken.com/'
        self.api_token = os.getenv('KRAKEN_API_TOKEN')
        self.api_sec = os.getenv('KRAKEN_API_SEC')

    def _get_kraken_signature(self, urlpath, data, secret):
        return base64.b64encode(
                hmac.new(
                    base64.b64decode(secret),
                    urlpath.encode() + hashlib.sha256(
                        (str(data['nonce']) + urllib.parse.urlencode(data)).encode()
                        ).digest(),
                    hashlib.sha512
                    ).digest()).decode()

    def _kraken_request(self, uri_path, data):
        return requests.post(
                (self.api_url + uri_path),
                headers = {
                    'API-Key': self.api_sec,
                    'API-Sign': self._get_kraken_signature(uri_path, data, self.api_sec)
                    },
                data=data
                ).json()

    def get_account_balance(self):
        return self._kraken_request('/0/private/Balance', {'nonce': str(int(1000*time.time()))})

    def add_order(self, order):
        return self._kraken_request('/0/private/AddOrder', dict(order))

    def ohlc(self, asset_pair):
       return requests.get(f'{self.api_url}/0/public/OHLC?pair={asset_pair}').json()
