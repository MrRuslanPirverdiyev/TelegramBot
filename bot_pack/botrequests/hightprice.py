import os
import re
import telebot
from loguru import logger
from typing import Optional
from datetime import datetime, date
from bot_pack.botrequests.locations import Location
from bot_pack.botrequests.hotels import Hotels
from bot_pack.botrequests.all_foto_hotels import FotoHotels
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from bot_pack.botrequests.user_chat_log import UserManager


class Hightprice:
    """
    Класс Hightprice: Для отправки на поиск города по запросу юзера по убыванию.
        Методы:
            find_hotels:
                Обрабатывает запросы юзера и отправляет их на нахождение данных в АПИ
            calendar_call_in и calendar_call_out:
                Для вызова календаря
            results:
                Обрабатывает данные календаря и отправляет на поиск отеля
            find_fotos:
                Для выводе фото по ID отеля
            pag:
                Для вызова пагинации фото
            pag_hotels_hight:
                Для вызова пагинации отелей
            list_back_fotos:
                Для вызова метода удалении списка фото
            list_back_hotels:
                Для вызова метода удалении списка отелей
            loc_start:
                Для вызова метода вызова локации отеля
    """
    def __init__(self):
        self.rapid_api_token: str = os.getenv('RAPID_API')
        self.url: list = [
            "https://hotels4.p.rapidapi.com/locations/v2/search",
            "https://hotels4.p.rapidapi.com/properties/list",
            "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        ]
        self.headers: dict = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': self.rapid_api_token
        }
        self.location: Location = Location(self.rapid_api_token, self.url[0], self.headers)
        self.foto_hotels: Optional = None
        self.hotels: Hotels = Hotels()
        self.msg: Optional = None
        self.bot: Optional = None
        self.id_city: Optional = None
        self.data_us_base: Optional = None

    def find_hotels(self, msg: telebot.types.Message, bot: telebot.TeleBot, data_us_base: UserManager):
        self.msg = msg
        self.bot = bot
        self.data_us_base = data_us_base
        try:
            self.id_city: int = self.location.loc_id(user_msg=msg.text.title())
            self.calendar_call_in(bot=bot, msg=msg)
        except Exception:
            logger.exception('Сбой ID города')
            bot.send_message(msg.chat.id, 'Не смог найти город,нажмите /reset')

    @classmethod
    def calendar_call_in(cls, bot: telebot.TeleBot, msg: telebot.types.Message):
        step_key: dict = {'year': 'год'}
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
        bot.send_message(msg.chat.id,
                         f"Дата заезда: {step_key[LSTEP[step]]}",
                         reply_markup=calendar
                         )

    def calendar_call_out(self):
        step_key: dict = {'year': 'год'}
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).build()
        self.bot.send_message(self.msg.chat.id,
                              f"Дата выезда: {step_key[LSTEP[step]]}",
                              reply_markup=calendar
                              )

    def results(self, check_in: str, check_out: str):
        try:
            now: list = re.findall(r'\w+', datetime.now().strftime('%Y-%m-%d'))
            in_data: list = re.findall(r'\w+', str(check_in))
            out_data: list = re.findall(r'\w+', str(check_out))
            if in_data[0] < now[0]:
                self.bot.send_message(self.msg.chat.id, 'Извините,я не могу вернутся в прошлое')
                self.calendar_call_in(self.bot, self.msg)

            elif in_data[0] == now[0] and in_data[1] < now[1]:
                self.bot.send_message(self.msg.chat.id, 'Извините,я не могу вернутся в прошлое')
                self.calendar_call_in(self.bot, self.msg)

            elif in_data[0] == now[0] and in_data[1] == now[1] and in_data[2] < now[2]:
                self.bot.send_message(self.msg.chat.id, 'Извините,я не могу вернутся в прошлое')
                self.calendar_call_in(self.bot, self.msg)

            elif out_data[0] < in_data[0]:
                self.bot.send_message(self.msg.chat.id, 'Извините,дата выезда указано не правильно')
                self.calendar_call_in(self.bot, self.msg)

            elif out_data[0] == in_data[0] and out_data[1] < in_data[1]:
                self.bot.send_message(self.msg.chat.id, 'Извините,дата выезда указано не правильно')
                self.calendar_call_in(self.bot, self.msg)

            elif out_data[0] == in_data[0] and out_data[1] == in_data[1] and out_data[2] <= in_data[2]:
                self.bot.send_message(self.msg.chat.id, 'Извините,дата выезда указано не правильно')
                self.calendar_call_in(self.bot, self.msg)

            else:
                date_1: list = re.findall(r'\w+', str(check_in))
                date_2: list = re.findall(r'\w+', str(check_out))
                count_days: str = str(date(int(date_2[0]), int(date_2[1]), int(date_2[2])) -
                                      date(int(date_1[0]), int(date_1[1]), int(date_1[2]))).split()[0]
                if self.id_city is not None:
                    self.hotels.hotels_call(
                        self.id_city,
                        self.msg,
                        self.bot,
                        self.rapid_api_token,
                        self.url[1],
                        self.headers,
                        self.data_us_base,
                        check_in,
                        check_out,
                        count_days,
                        sort="PRICE_HIGHEST_FIRST",
                        minimal='',
                        maximal=''
                    )
                else:
                    self.bot.send_message(self.msg.chat.id, 'Не смог найти такой город')
        except Exception:
            logger.exception('Ошибка при отправки данных из results в hotels')
            self.bot.send_message(self.msg.chat.id, 'Програмная ошибка, нажмите /reset')

    def find_fotos(self, call_bot: telebot.types.CallbackQuery, bot_token: telebot.TeleBot, hotel_id: str):
        try:
            self.foto_hotels: FotoHotels = FotoHotels(
                hotelId=hotel_id,
                call=call_bot,
                bot=bot_token,
                rapid_token=self.rapid_api_token,
                url=self.url[2],
                head_ers=self.headers
            )
            self.foto_hotels.get_foto()
        except Exception:
            logger.exception('Ошибка при отправки данных из find_fotos в foto_hotels.get_foto')
            self.bot.send_message(self.msg.chat.id, 'Програмная ошибка, нажмите /reset')

    def pag(self, pages: str):
        try:
            self.foto_hotels.pag_foto(int(pages))
        except Exception:
            logger.exception('Ошибка при отправки данных из pag в foto_hotels.pag_foto')
            self.bot.send_message(self.msg.chat.id, 'Програмная ошибка, нажмите /reset')

    def pag_hotels_hight(self, pages: str):
        try:
            self.hotels.pag_hotels(int(pages))
        except Exception:
            logger.exception('Ошибка при отправки данных из pag_hotels_hight в hotels.pag_hotels')
            self.bot.send_message(self.msg.chat.id, 'Програмная ошибка, нажмите /reset')

    def list_back_hotels(self):
        try:
            if self.msg is not None:
                self.hotels.zero_list(self.msg)
        except Exception:
            logger.exception('Ошибка при отправки данных из list_back_hotels в hotels.zero_lists')

    def list_back_fotos(self):
        try:
            if self.msg is not None and self.foto_hotels is not None:
                self.foto_hotels.zero_list(self.msg)
        except Exception:
            logger.exception('Ошибка при отправки данных из list_back_fotos в foto_hotels.zero_list')

    def loc_start(self, callback_loc_lat: str, callback_loc_lon: str):
        try:
            if self.hotels is not None:
                self.hotels.loc_in_map(callback_loc_lat, callback_loc_lon)
        except Exception:
            logger.exception('Ошибка при отправки данных из loc_start в hotels.loc_in_map')
