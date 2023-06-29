from sys import stderr
from loguru import logger
from multiprocessing.dummy import current_process


def log(address):
    try:
        logger.remove()
        logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                                  ' | <level>{level: <2}</level>'
                                  f' | <level>{address}</level>'
                                  ' | <level>{message}</level>')
    except:
        pass
    logger.add(f'Logs.log')
    return logger


if __name__ == '__main__':
    pass
