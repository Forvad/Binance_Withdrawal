from random import randint, uniform
from time import sleep
import ccxt
from tqdm import tqdm

import config
from ccxt.base.errors import InsufficientFunds
from Logs.Loging import log


def sleeping(from_sleep, to_sleep):
    x = randint(from_sleep, to_sleep)
    for _ in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        sleep(1)


def binance_withdraw(address):
    try:
        exchange = ccxt.binance({
            'apiKey': config.api_key,
            'secret': config.secret_key,
            'enableRateLimit': False,
            'options': {
                'defaultType': 'spot'
            }
        })
        rand = {1: randint, 2: uniform}
        value = rand[config.randoms](config.value[0], config.value[1])
        if isinstance(value, float):
            value = round(value, 4)
        exchange.withdraw(
            code=config.token,
            amount=value,
            address=address,
            tag=None,
            params={
                "network": config.ntwork
            }
        )
        log(address).success(f'The output is successful token({config.token}), value({value})')

    except InsufficientFunds as error:
        if str(error) == 'binance {"code":-4026,"msg":"User has insufficient balance"}':
            log(address).error(f'Not enough balance - {address}')
    except BaseException as error:
        log(address).error(error)


def wallet() -> list:
    with open('wallet.txt', 'r') as file:
        wallets = file.read().splitlines()
        return wallets


def main():
    wallets = wallet()
    for address in wallets:
        binance_withdraw(address)
        sleeping(config.Delay[0], config.Delay[1])


if __name__ == "__main__":
   main()
