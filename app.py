import numpy

from dotenv import load_dotenv
from Kraken import Kraken
from scipy import stats

load_dotenv()

kraken = Kraken()
raw = {
        asset: {
            asset_pair: kraken.ohlc(asset_pair) for asset_pair in kraken.ASSET_PAIRS[asset]
            } for asset in kraken.ASSETS
        }
processed = {
        asset: {
            asset_pair: {
                'time': numpy.array(
                    [int(each[0]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'open': numpy.array(
                    [float(each[1]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'high': numpy.array(
                    [float(each[2]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'low': numpy.array(
                    [float(each[3]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'close': numpy.array(
                    [float(each[4]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'volume': numpy.array(
                    [float(each[5]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
					),
                'count': numpy.array(
                    [float(each[6]) for each in raw[asset][asset_pair]['result'][kraken.ASSET_PAIRS[asset][asset_pair]]]
                    )
                } for asset_pair in kraken.ASSET_PAIRS[asset]
            } for asset in kraken.ASSETS
        }
linregresses = {
        asset: {
            asset_pair: {
                'open': stats.linregress(
                    processed[asset][asset_pair]['time'],
                    processed[asset][asset_pair]['open']
                    ),
                'high': stats.linregress(
                    processed[asset][asset_pair]['time'],
                    processed[asset][asset_pair]['high']
                    ),
                'low': stats.linregress(
                    processed[asset][asset_pair]['time'],
                    processed[asset][asset_pair]['low']
                    ),
                'close': stats.linregress(
                    processed[asset][asset_pair]['time'],
                    processed[asset][asset_pair]['close']
                    )
                } for asset_pair in kraken.ASSET_PAIRS[asset]
            } for asset in kraken.ASSETS
        }
slopes = {
        asset: {
            asset_pair: {
                'open': linregresses[asset][asset_pair]['open'].slope,
                'high': linregresses[asset][asset_pair]['high'].slope,
                'low': linregresses[asset][asset_pair]['low'].slope,
                'close': linregresses[asset][asset_pair]['close'].slope
                } for asset_pair in kraken.ASSET_PAIRS[asset]
            } for asset in kraken.ASSETS
        }
averages = {
        asset: {
            asset_pair: sum(
                [slopes[asset][asset_pair][each] for each in slopes[asset][asset_pair]]
                )/4 for asset_pair in kraken.ASSET_PAIRS[asset]
            } for asset in kraken.ASSETS
        }
print(averages)
