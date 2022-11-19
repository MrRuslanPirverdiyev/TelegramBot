import sqlite3
from datetime import datetime
from loguru import logger
from typing import Optional


class UserManager:
    """
    Класс UserManager
    Принимает данные:
        индентификатор пользователя
        имя пользователя
        сообщения пользователя
        время отправки сообщения
    Записывает в базу индивидуально каждому пользователю свои данные и сообщения
    а также через геттер возвращает предыдущие запросы,у каждого пользователя свои
    """

    def __init__(self):
        self.__user_identity: Optional = None
        self.__conn: Optional = None
        self.__cursor: Optional = None
        self.sql_connect()

    def sql_connect(self):
        self.__conn = sqlite3.connect(r'F:\bot_telegram_python\all_users_data_base.db', check_same_thread=False)
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                user_id INT UNIQUE,
                user_name STRING NOT NULL,
                nick_name STRING,
                chat_log STRING,
                lowprice STRING,
                hightprice STRING,
                bestdeal STRING,
                best_price_end_dis STRING,
                states STRING
        )""")
        self.__conn.commit()

    def db_table_val(self, user_id: int, user_name: str, nick_name: str, log_text: str, tme: str):
        self.__user_identity = user_id
        try:
            exists = self.__cursor.execute('SELECT * FROM user_data WHERE user_id = ?', [user_id]).fetchone()
            text = 'id_in_data' if exists else 'id_not_data'
            for val in self.__conn.execute(f'SELECT chat_log FROM user_data WHERE user_id = {user_id}'):
                list_history: list = list(val[0].split('\n'))
                text_in: str = ''
                while len(list_history) > 20:
                    list_history.pop(1)

                for all_mess in list_history:
                    text_in += all_mess + '\n'

                log_text: str = str(text_in) + str(tme) + ' ' + str(log_text)

            if text == 'id_not_data':
                self.__cursor.execute(
                    """INSERT INTO user_data (user_id, user_name, nick_name, chat_log, lowprice, hightprice, bestdeal,  best_price_end_dis, states)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, user_name, nick_name, '', '', '', '', '', '')
                )
                self.__conn.commit()
            else:
                self.__cursor.execute(f'UPDATE user_data SET chat_log = "{log_text}" WHERE user_id = {user_id}')
                self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при создании БД')

    def del_data(self, user_id: int):
        try:
            self.__cursor.execute(f'UPDATE user_data SET chat_log = "" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при удалении данных из chat_log БД')

    def del_data_best_loc_pr_dis(self, user_id: int):
        try:
            self.__cursor.execute(f'UPDATE user_data SET best_price_end_dis = "" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при удалении данных из best_price_end_dis БД')

    def history_out(self, user_id: int):
        try:
            return self.__conn.execute(f'SELECT chat_log FROM user_data WHERE user_id = {user_id}')
        except Exception:
            logger.exception('Ошибка при выводе данных из chat_log БД')

    def low_price_hist_out(self, user_id: int):
        try:
            return self.__conn.execute(f'SELECT lowprice FROM user_data WHERE user_id = {user_id}')
        except Exception:
            logger.exception('Ошибка при выводе данных из lowprice БД')

    def hight_price_hist_out(self, user_id: int):
        try:
            return self.__conn.execute(f'SELECT hightprice FROM user_data WHERE user_id = {user_id}')
        except Exception:
            logger.exception('Ошибка при выводе данных из hightprice БД')

    def bestdeal_hist_out(self, user_id: int):
        try:
            return self.__conn.execute(f'SELECT bestdeal FROM user_data WHERE user_id = {user_id}')
        except Exception:
            logger.exception('Ошибка при выводе данных из bestdeal БД')

    def bestdeal_hist_loc_pr_dis_out(self, user_id: int):
        try:
            return self.__conn.execute(f'SELECT best_price_end_dis FROM user_data WHERE user_id = {user_id}')
        except Exception:
            logger.exception('Ошибка при выводе данных из bestdeal_hist_loc_pr_dis_out БД')

    def low_price_base(self, user_id: int, name_hotel: str):
        time_real: str = datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
        try:
            for val in self.__conn.execute(f'SELECT lowprice FROM user_data WHERE user_id = {user_id}'):
                list_history: list = list(val[0].split('\n'))
                text_low: str = ''
                while len(list_history) > 100:
                    for _ in range(5):
                        list_history.pop(1)

                for all_mess in list_history:
                    text_low += all_mess + '\n'

                name_hotel = str(text_low) + str(time_real) + '\n' + str(name_hotel) + '\n'
            self.__cursor.execute(f'UPDATE user_data SET lowprice = "{name_hotel}" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при добавлении в lowprice БД')

    def hight_price_base(self, user_id: int, name_hotel: str):
        time_real: str = datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
        try:
            for val in self.__conn.execute(f'SELECT hightprice FROM user_data WHERE user_id = {user_id}'):
                list_history: list = list(val[0].split('\n'))
                text_hight: str = ''
                while len(list_history) > 100:
                    for _ in range(5):
                        list_history.pop(1)

                for all_mess in list_history:
                    text_hight += all_mess + '\n'

                name_hotel = str(text_hight) + str(time_real) + '\n' + str(name_hotel) + '\n'
            self.__cursor.execute(f'UPDATE user_data SET hightprice = "{name_hotel}" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при добавлении в hightprice БД')

    def bestdeal_base(self, user_id: int, name_hotel: str):
        time_real: str = datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
        try:
            for val in self.__conn.execute(f'SELECT bestdeal FROM user_data WHERE user_id = {user_id}'):
                list_history: list = list(val[0].split('\n'))
                text_hight: str = ''
                while len(list_history) > 100:
                    for _ in range(5):
                        list_history.pop(1)

                for all_mess in list_history:
                    text_hight += all_mess + '\n'

                name_hotel = str(text_hight) + str(time_real) + '\n' + str(name_hotel) + '\n'
            self.__cursor.execute(f'UPDATE user_data SET bestdeal = "{name_hotel}" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при добавлении в bestdeal БД')

    def bestdeal_loc_pr_dis_base(self, user_id: int, name_hotel: str):
        try:
            for val in self.__conn.execute(f'SELECT best_price_end_dis FROM user_data WHERE user_id = {user_id}'):
                list_history: list = list(val[0].split('\n'))
                text_hight: str = ''

                for all_mess in list_history:
                    text_hight += all_mess + '\n'

                name_hotel = str(text_hight) + str(name_hotel)
            self.__cursor.execute(f'UPDATE user_data SET best_price_end_dis = "{name_hotel}" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при добавлении в best_price_end_dis БД')

    def states_write(self, user_id: int, state_val: str):
        try:
            self.__cursor.execute(f'UPDATE user_data SET states = "{state_val}" WHERE user_id = {user_id}')
            self.__conn.commit()
        except Exception:
            logger.exception('Ошибка при добавлении в states БД')

    def get_states(self, user_id: int):
        try:
            for val in self.__conn.execute(f'SELECT states FROM user_data WHERE user_id = {user_id}'):
                return str(val[0])
        except Exception:
            logger.exception('Ошибка при выводе данных из states БД')
