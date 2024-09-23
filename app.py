import logging
import os

from kraken_bot.KrakenBot import KrakenBot
from kraken_bot.LinearRegression import LinearRegression
from kraken_bot.MyStrategy import MyStrategy
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

model = LinearRegression(
        r_value_target = float(os.getenv('R_VALUE_TARGET'))
        )
strategy = MyStrategy(
        investment_count = int(os.getenv('INVESTMENT_COUNT')),
        investment_volume = float(os.getenv('INVESTMENT_VOLUME'))
        )
bot = KrakenBot(
        token = os.getenv('KRAKEN_API_TOKEN'),
        secret = os.getenv('KRAKEN_API_SEC'),
        tier = 'Pro',
        model = model,
        trading_strategy = strategy
        )

if __name__ == '__main__':
    bot.update(full=True)
    bot.execute()
