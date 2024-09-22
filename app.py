import logging
import os

from kraken_bot.KrakenBot import KrakenBot
from kraken_bot.LinearRegression import LinearRegression
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

bot = KrakenBot(
        token = os.getenv('KRAKEN_API_TOKEN'),
        secret = os.getenv('KRAKEN_API_SEC'),
        tier = 'Pro',
        investment_count = int(os.getenv('INVESTMENT_COUNT')),
        investment_volume = float(os.getenv('INVESTMENT_VOLUME'))
        )
model = LinearRegression(
        r_value_target = float(os.getenv('R_VALUE_TARGET'))
        )

if __name__ == '__main__':
    bot.update()
    bot.trade(model)
