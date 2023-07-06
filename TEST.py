from requests import get
from Logs.Loging import log
import time


def get_prices(chain, address):
    prices = {'arbitrum': 'ETH', 'optimism': 'ETH', 'avalanche': 'AVAX', 'polygon': 'MATIC',
              'btc': 'BTC', 'metis': 'METIS', 'bsc': 'BNB', 'harmony': 'ONE', 'coredao': 'CORE',
              'moonriver': 'MOVR', 'fantom': 'FTM'}
    symbol = prices[chain]
    try:
        response = get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT')
        if response.status_code != 200:
            log(address).info('Limit on the number of requests, we sleep for 30 seconds')
            log(address).info(f"status_code = {response.status_code}, text = {response.text}")
            time.sleep(30)
            return get_prices(chain, address)
        log('').info(f'f"status_code = {response.status_code}, text = {response.text}, symbol = {symbol}')
        result = [response.json()]
        price = result[0]['USDT']
        return price
    except BaseException as error:
        log(address).error(error)


if __name__ == '__main__':
    network = ['polygon', 'avalanche', 'optimism', 'arbitrum', 'bsc', 'harmony', 'moonriver']
    for i in network:
        get_prices(i, 'binance')
