import time

import ccxt
from main import sleeping
from config import network_steable, network_native, api_key_STG, secret_key_STG, value_steable, value_native,\
    WITHDRAVAL_NATIVE, WITHDRAVAL_STEABLE, Delay_STG, AUTO_BUY
from random import choice, randint, uniform
from Logs.Loging import log
from ccxt.base.errors import InsufficientFunds
from requests import get
from ONE_converter import convert_eth_to_one
from binance.spot import Spot


name_native = {'bsc': 'BNB',
               'avalanche': 'AVAX',
               'polygon': 'MATIC',
               'optimism': 'ETH',
               'arbitrum': 'ETH',
               'moonriver': 'MOVR',
               'harmony': 'ONE',
               "fantom": "FTM"
               }

#
# def get_prices(chain, address):
#     prices = {'arbitrum': 'ETH', 'optimism': 'ETH', 'avalanche': 'AVAX', 'polygon': 'MATIC',
#               'btc': 'BTC', 'metis': 'METIS', 'bsc': 'BNB', 'harmony': 'ONE', 'coredao': 'CORE',
#               'moonriver': 'MOVR', 'fantom': 'FTM'}
#     symbol = prices[chain]
#     try:
#         response = get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT')
#         if response.status_code != 200:
#             log(address).info('Limit on the number of requests, we sleep for 30 seconds')
#             log(address).info(f"status_code = {response.status_code}, text = {response.text}")
#             time.sleep(30)
#             return get_prices(chain, address)
#         result = [response.json()]
#         price = result[0]['USDT']
#         return price
#     except BaseException as error:
#         log(address).error(error)


def get_prices(chain, address):
    prices = {'arbitrum': 'ETH', 'optimism': 'ETH', 'avalanche': 'AVAX', 'polygon': 'MATIC',
              'btc': 'BTC', 'metis': 'METIS', 'bsc': 'BNB', 'harmony': 'ONE', 'coredao': 'CORE',
              'moonriver': 'MOVR', 'fantom': 'FTM'}
    symbol = prices[chain]
    try:
        response = get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT')
        if response.status_code != 200:
            log(address).info('Limit on the number of requests, we sleep for 30 seconds')
            log(address).info(f"status_code = {response.status_code}, text = {response.text}")
            time.sleep(30)
            return get_prices(chain, address)
        result = response.json()
        price = round(float(result['price']), 4)
        return price
    except BaseException as error:
        log(address).error(error)


def binance_withdraw(address: str, token: str, network: str) -> None:
    name_network = {'bsc': 'BSC',
                    'avalanche': 'AVAXC',
                    'polygon': 'MATIC',
                    'optimism': 'OPTIMISM',
                    'arbitrum': 'ARBITRUM',
                    'moonriver': 'MOVR',
                    'harmony': 'ONE',
                    'fantom': "FTM"
                    }
    try:
        exchange = ccxt.binance({
            'apiKey': api_key_STG,
            'secret': secret_key_STG,
            'enableRateLimit': False,
            'options': {
                'defaultType': 'spot'
            }
        })
        if token in ['USDT', 'USDC', 'BUSD']:
            balance = get_balance()
            value = randint(value_steable[0], value_steable[1])
            if AUTO_BUY:
                if balance[token] < value:
                    amount = value - balance[token]
                    amount = amount if amount >= 11 else 11
                    buy_token(token, int(amount))
                    log("binance").success(f"buy {amount} {token}")
                    time.sleep(3)

        else:
            value = uniform(value_native[0], value_native[1])
            value /= get_prices(network, address)
            token = name_native[token]
            value = round(value, 4)
            if token == 'ONE':
                address = convert_eth_to_one(address)
        exchange.withdraw(
            code=token,
            amount=value,
            address=address,
            params={
                "network": name_network[network]
            }
        )
        log(address).success(f'The output is successful token({token}), value({value})'
                             f', network({name_network[network]})')

    except InsufficientFunds as error:
        if str(error) == 'binance {"code":-4026,"msg":"User has insufficient balance"}':
            log(address).error(f'Not enough balance - {address}')
            time.sleep(10)
            binance_withdraw(address, token, network)
    except BaseException as error:
        log(address).error(error)


def wallet() -> list:
    with open('wallet.txt', 'r') as file:
        wallets = file.read().splitlines()
        return wallets


def work():
    steable = {'polygon': ['USDC'],
               'bsc': ['BUSD', 'USDT'],
               'arbitrum': ['USDT'],
               'optimism': ['USDC'],
               'avalanche': ['USDT']}

    wallets = wallet()
    if AUTO_BUY:
        auto_buy()
    for address in wallets:
        network_work_steable = choice(network_steable)
        steable_work = choice(steable[network_work_steable])
        if WITHDRAVAL_STEABLE:
            binance_withdraw(address, steable_work, network_work_steable)
            sleeping(Delay_STG[0], Delay_STG[1])
        if WITHDRAVAL_NATIVE:
            for chain in network_native:
                binance_withdraw(address, chain, chain)
                sleeping(Delay_STG[0], Delay_STG[1])


def buy_token(token, value):
    print(token, value)
    client = Spot(api_key=api_key_STG,
                  api_secret=secret_key_STG)

    params = {
        'symbol': f'{token}USDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': value,
    }

    client.new_order(**params)


def get_balance():
    client = Spot(api_key=api_key_STG,
                  api_secret=secret_key_STG)

    dd = client.account()
    tokens = {}
    token = dd['balances']
    for i in token:
        if i['asset'] in ['MATIC', 'USDT', 'USDC', 'BUSD', 'AVAX', 'ETH', 'BNB', 'ONE', 'MOVR', "FTM"]:
            tokens[i['asset']] = float(i['free'])
    return tokens


def auto_buy():
    wallets_all = len(wallet())
    balance = get_balance()
    ETH_dabl = True
    for network in network_native:
        value = value_native[1] * wallets_all / get_prices(network, "binance")
        if 'arbitrum' in network_native and 'optimism' in network_native and network in ['arbitrum', 'optimism']:
            balance = get_balance()
            time.sleep(1)
            if ETH_dabl:
                value = value_native[1] * wallets_all / get_prices(network, "binance") * 2
                ETH_dabl = False

        if value > balance[name_native[network]]:
            if network in ['bsc', 'optimism', 'arbitrum']:
                decimal = 3
            elif network in ['harmony', "fantom"]:
                decimal = 0
            else:
                decimal = 2
            coin = name_native[network]
            value_coin = round(value - balance[name_native[network]], decimal)
            min_limit = round(12 / get_prices(network, "binance"), decimal)
            if value_coin < min_limit:
                value_coin = min_limit
            log("").info(f"{coin, value_coin}")
            buy_token(coin, value_coin)
            log("binance").success(f"buy {value_coin} {coin}")
            time.sleep(5)


if __name__ == '__main__':
    work()
