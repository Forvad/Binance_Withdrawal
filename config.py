api_key = ""

secret_key = ""

token = 'USDT'  # токен вывода

ntwork = 'MATIC'  # сеть вывода

value = [10, 12]  # Объём вывода мин - мах

Delay = [30, 60]  # задержка в сек

randoms = 2  # 1 рандом целых чисел, 2 - с десятыми


# STG module


api_key_STG = ""

secret_key_STG = ""

WITHDRAVAL_NATIVE = True  # вывод натива

WITHDRAVAL_STEABLE = False  # вывод стейбла

AUTO_BUY = True  # Авто докупка монет, за USDT

steable = {'polygon': ['USDT'],
           'bsc': ['USDT'],
           'arbitrum': ['USDT'],
           'optimism': ['USDT'],
           'avalanche': ['USDT'],
           "fantom": ["USDT"]}

# Сети вывода нейтива 'polygon', 'avalanche', 'optimism', 'arbitrum', 'bsc'
network_steable = ['avalanche']  # Выбор 1 рандом сети для вывода стейбла

# Сети вывода нейтива 'polygon', 'avalanche', 'optimism', 'arbitrum', 'bsc', 'harmony', 'moonriver'
# Раскидывает во все выбранные сети нейтив
network_native = ['fantom']

value_steable = [1, 3]  # Объём вывода мин - мах стейбла

value_native = [3.5, 4]  # Объём вывода мин - мах нейтива в $

Delay_STG = [30, 60]  # задержка в сек
