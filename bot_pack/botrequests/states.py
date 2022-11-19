from enum import Enum


class States(Enum):
    """
    Тут будем использовать строки (str)
    Возвращает значени определённого ключа
    """
    S_START = "0"
    S_RUN = "1"
    S_LOWPRICE = "2"
    S_HIGHPRICE = "3"
    S_BESTDEAL = "4"
    S_HISTORY = '5'
    S_LOW_FINDOTEL = '6'
    S_HIGHT_FINDOTEL = '7'
    S_BEST_FINDOTEL = '8'
    S_LOW_FOTOOTEL = '9'
    S_HIGHT_FOTOOTEL = '10'
    S_BEST_FOTOOTEL = '11'
    S_LOW_GOOGLEMAP = '12'
    S_HIGHT_GOOGLEMAP = '13'
    S_BEST_GOOGLEMAP = '14'
    S_HELP = '15'
    S_FICCHA = '16'
    S_BESTDEAL_PRICE = '17'
    S_BESTDEAL_DIS = '18'
    S_RESTART = '19'
