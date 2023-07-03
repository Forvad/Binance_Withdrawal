import ccxt
from main import sleeping
from config import network_steable, network_native, api_key_STG, secret_key_STG, value_steable, value_native,\
    WITHDRAVAL_NATIVE, WITHDRAVAL_STEABLE, Delay_STG
from random import choice, randint, uniform
from Logs.Loging import log
from ccxt.base.errors import InsufficientFunds
from requests import get
from ONE_converter import convert_eth_to_one
from binance.spot import Spot


def get_prices(chain, address):
    prices = {'arbitrum': 'ETH', 'optimism': 'ETH', 'avalanche': 'AVAX', 'polygon': 'MATIC',
              'btc': 'BTC', 'metis': 'METIS', 'bsc': 'BNB', 'harmony': 'ONE', 'coredao': 'CORE',
              'moonriver': 'MOVR', 'fantom': 'FTM'}
    symbol = prices[chain]
    try:
        response = get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT')
    except BaseException as error:
        log(address).error(f'Error Get request price token: {error}')
        raise BaseException('Error Get request price token')
    try:
        result = [response.json()]
        price = result[0]['USDT']
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
                    }
    name_native = {'bsc': 'BNB',
                   'avalanche': 'AVAX',
                   'polygon': 'MATIC',
                   'optimism': 'ETH',
                   'arbitrum': 'ETH',
                   'moonriver': 'MOVR',
                   'harmony': 'ONE',
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
            value = randint(value_steable[0], value_steable[1])
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
            tag=None,
            params={
                "network": name_network[network]
            }
        )
        log(address).success(f'The output is successful token({token}), value({value})')

    except InsufficientFunds as error:
        if str(error) == 'binance {"code":-4026,"msg":"User has insufficient balance"}':
            log(address).error(f'Not enough balance - {address}')
    except BaseException as error:
        log(address).error(error)


def wallet() -> list:
    with open('wallet.txt', 'r') as file:
        wallets = file.read().splitlines()
        return wallets


def work():
    steable = {'polygon': ['USDC'],
               'bsc': ['BUSD', 'USDT'],
               'armibtrum': ['USDT', 'USDC'],
               'optimism': ['USDC'],
               'avalanche': ['USDC', 'USDT']}

    wallets = wallet()
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
    client = Spot(api_key=api_key_STG,
                  api_secret=secret_key_STG)


    # Get account and balance information
    # dd = client.account()
    # token = dd['balances']
    # for i in token:
    #     if i['asset'] in ['MATIC', 'USDT']:
    #         print(i['free'])

    params = {
        'symbol': f'{token}USDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': value,
    }

    response = client.new_order(**params)


if __name__ == '__main__':
    work()
