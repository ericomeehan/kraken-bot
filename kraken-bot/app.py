import os

from KrakenBot import KrakenBot
from dotenv import load_dotenv

load_dotenv()
bot = KrakenBot(
        kraken_api_token = os.getenv('KRAKEN_API_TOKEN'),
        kraken_api_sec = os.getenv('KRAKEN_API_SEC'),
        tier = 'Pro',
        r_value_target = float(os.getenv('R_VALUE_TARGET')),
        investment_count = int(os.getenv('INVESTMENT_COUNT')),
        investment_volume = float(os.getenv('INVESTMENT_VOLUME'))
        )

if __name__ == '__main__':
    bot.update()
