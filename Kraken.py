import base64
import hashlib
import hmac
import os
import requests
import time
import urllib.parse

class Kraken():
    ASSET_PAIRS = {
            'XBTUSD': 'XXBTZUSD'
            }

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
                )

    def get_account_balance(self):
        return self._kraken_request('/0/private/Balance', {'nonce': str(int(1000*time.time()))})

    def ohlc(self, asset_pair):
        resp = requests.get(f'{self.api_url}/0/public/OHLC?pair={asset_pair}').json()
        return {
                'time': [int(each[0]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'open': [float(each[1]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'high': [float(each[2]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'low': [float(each[3]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'close': [float(each[4]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'volume': [float(each[5]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]],
                'count': [float(each[6]) for each in resp['result'][self.ASSET_PAIRS[asset_pair]]]
                }
