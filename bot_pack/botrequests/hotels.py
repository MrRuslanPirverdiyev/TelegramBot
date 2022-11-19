import requests
import json
import re
import validators
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
from bot_pack.botrequests.states import States
from loguru import logger
from typing import Optional
from bot_pack.botrequests.user_chat_log import UserManager


class Hotels:
    """
    Класс Hotels: Нужен для поиска отеля по ID города,сохраняет в виде списка в словаре по ID юзера.
    Методы:
        hotels_call:
            Осуществляет поиск и записывает результат
        pag_hotels:
            для пролистывания найденыых отелей
        zero_list:
            Для удаления данных из списка в словаре по ID
        loc_in_map:
            Для вывода локации определённого отеля
    """
    def __init__(self):
        self.destinationId = dict()
        self.bot: Optional = None
        self.mes: Optional = None
        self.rapid_token: Optional = None
        self.url: Optional = None
        self.headers: Optional = None
        self.data_base: Optional = None
        self.call_del_status: str = ''
        self.all_hotels_dict = dict()
        self.new_res = list()

    def hotels_call(
            self,
            des_id: int,
            mes: telebot.types.Message,
            bot_tok: telebot.TeleBot,
            rapid_token: str,
            url_val: str,
            headers_val: dict,
            base_val: UserManager,
            date_in: str,
            date_out: str,
            count_price,
            sort: str,
            minimal: Optional = '',
            maximal: Optional = '',
            dis_value: Optional = None
    ):
        self.all_hotels_dict[mes.chat.id] = []
        self.destinationId[mes.chat.id] = des_id
        self.mes = mes
        self.bot = bot_tok
        self.rapid_token = rapid_token
        self.url = url_val
        self.headers = headers_val
        self.data_base = base_val
        querystring = {
                       "destinationId": self.destinationId[mes.chat.id],
                       "pageNumber": "1",
                       "pageSize": "25",
                       "checkIn": date_in,
                       "checkOut": date_out,
                       "adults1": "1",
                       "sortOrder": sort,
                       "locale": "ru_RU",
                       "currency": "USD",
                       "priceMin": minimal,
                       "priceMax": maximal
        }
        try:
            response: requests = requests.request("GET", self.url, headers=self.headers, params=querystring)
            data: json = json.loads(response.text)
            len_list_data: int = len(data["data"]["body"]["searchResults"]["results"])
            for i in range(len_list_data - 1):
                try:
                    if validators.url(data["data"]["body"]["searchResults"]["results"][i]["optimizedThumbUrls"]["srpDesktop"]):
                        self.all_hotels_dict[mes.chat.id].append({
                            'id': data["data"]["body"]["searchResults"]["results"][i]["id"],
                            'name': data["data"]["body"]["searchResults"]["results"][i]["name"],
                            'address': data["data"]["body"]["searchResults"]["results"][i]["address"]["streetAddress"],
                            'landmarks': data["data"]["body"]["searchResults"]["results"][i]["landmarks"],
                            'ratePlan': data["data"]["body"]["searchResults"]["results"][i]["ratePlan"]["price"]["current"],
                            'foto_url': data["data"]["body"]["searchResults"]["results"][i]["optimizedThumbUrls"]["srpDesktop"],
                            'coordinate_lat': data["data"]["body"]["searchResults"]["results"][i]["coordinate"]["lat"],
                            'coordinate_lon': data["data"]["body"]["searchResults"]["results"][i]["coordinate"]["lon"],
                            'count_days': count_price
                        })
                except Exception:
                    logger.debug('Пропуск отелей,отсутсвует либо цена либо же адрес')
            self.bot.send_message(self.mes.chat.id, 'Вот что я смог найти')
            if self.data_base.get_states(self.mes.chat.id) == States.S_LOW_FINDOTEL.value or \
                    self.data_base.get_states(self.mes.chat.id) == States.S_HIGHT_FINDOTEL.value:
                self.pag_hotels(page=1)
            elif self.data_base.get_states(self.mes.chat.id) == States.S_BEST_FINDOTEL.value:
                for list_res in self.all_hotels_dict[mes.chat.id]:
                    dis_val = list_res['landmarks'][0]['distance']
                    float_dis_val = re.sub(r',', '.', dis_val[:len(dis_val) - 3])
                    if float(dis_value[0]) <= float(float_dis_val) <= float(dis_value[1]):
                        self.new_res.append(list_res)

                self.all_hotels_dict[mes.chat.id]: list = self.new_res
                self.new_res: list = []
                if len(self.all_hotels_dict[mes.chat.id]) > 0:
                    self.pag_hotels(page=1)
                else:
                    self.bot.send_message(self.mes.chat.id, 'Ничего не найдено')

        except Exception:
            logger.exception('Ошибка при выводе отелей')
            self.bot.send_message(self.mes.chat.id, 'Что-то пошло не так,повторите попытку,нажмите /reset')

    def pag_hotels(self, page: int):
        try:
            text: str = \
                '🌁 Название - {} ' \
                '\n📍 Адрес - {} ' \
                '\n🚶‍♀️Дистанция от центра города - {} ' \
                '\n💰 Цена за одну ночь - {} ' \
                '\n💰 Цена за выбранный промежуток - ${} ' \
                '\n🔎 Ссылка - https://hotels.com/ho{}'.format(
                    self.all_hotels_dict[self.mes.chat.id][page - 1]['name'],
                    self.all_hotels_dict[self.mes.chat.id][page - 1]['address'],
                    self.all_hotels_dict[self.mes.chat.id][page - 1]['landmarks'][0]['distance'],

                    self.all_hotels_dict[self.mes.chat.id][page - 1]['ratePlan'],
                    int(self.all_hotels_dict[self.mes.chat.id][page - 1]['count_days']) *
                    int(self.all_hotels_dict[self.mes.chat.id][page - 1]['ratePlan'].split('$')[1]),
                    self.all_hotels_dict[self.mes.chat.id][page - 1]['id']
                )
            if self.data_base.get_states(self.mes.chat.id) == States.S_LOW_FINDOTEL.value:
                self.data_base.low_price_base(self.mes.chat.id, text)
            elif self.data_base.get_states(self.mes.chat.id) == States.S_HIGHT_FINDOTEL.value:
                self.data_base.hight_price_base(self.mes.chat.id, text)
            elif self.data_base.get_states(self.mes.chat.id) == States.S_BEST_FINDOTEL.value:
                self.data_base.bestdeal_base(self.mes.chat.id, text)
            url: list = re.findall(
                r'.{84}',
                self.all_hotels_dict[self.mes.chat.id][page - 1]['foto_url']
            )
            paginator: InlineKeyboardPaginator = InlineKeyboardPaginator(
                len(self.all_hotels_dict[self.mes.chat.id]) - 1,
                current_page=page,
                data_pattern='hotels#{page}'
            )
            paginator.add_before(
                telebot.types.InlineKeyboardButton(
                    'Показать все фото',
                    callback_data='[{},{}]'.format(
                        '/foto_gallery',
                        self.all_hotels_dict[self.mes.chat.id][page - 1]['id']
                    )),

                telebot.types.InlineKeyboardButton(
                    'Карта',
                    callback_data='[{},{},{}]'.format(
                        '/google_map_holel',
                        self.all_hotels_dict[self.mes.chat.id][page - 1]['coordinate_lat'],
                        self.all_hotels_dict[self.mes.chat.id][page - 1]['coordinate_lon']
                    ))
            )

            paginator.add_after(telebot.types.InlineKeyboardButton(
                'Закрыть поиск отеля',
                callback_data='back_find_hotels'
            ))

            self.bot.send_photo(
                self.mes.chat.id,
                url[0],
                text,
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
        except Exception:
            logger.exception('Ошибка при пагинации отелей')
            self.all_hotels_dict[self.mes.chat.id].pop(page - 1)
            self.pag_hotels(page)

    def zero_list(self, msg: telebot.types.Message):
        try:
            if msg.chat.id in self.all_hotels_dict:
                if len(self.all_hotels_dict[msg.chat.id]) > 0:
                    self.all_hotels_dict[msg.chat.id] = []
        except Exception:
            return Exception

    def loc_in_map(self, loc_lat: str, loc_lon: str):
        try:
            keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(
                text='Закрыть карту',
                callback_data='/close_map_location'
            ))
            self.bot.send_location(
                self.mes.chat.id,
                latitude=float(loc_lat),
                longitude=float(loc_lon),
                reply_markup=keyboard
            )
        except Exception:
            return Exception
