import requests
import json
import telebot
import re
import validators
from telegram_bot_pagination import InlineKeyboardPaginator
from loguru import logger
from typing import Optional


class FotoHotels:
    """
    Класс FotoHotels: для поиска фото отелей
    Принимает данные:
        hotelId,
        call,
        bot,
        rapid_token,
        url,
        head_ers
    Методы:
        get_foto:
            Принимает ID отеля и добавляет найденный результат в список со словарём по ID юзера.
            Дальше вызывает метод pag_foto
        pag_foto:
            Нужен для пролистывания фото.
            Выводит урл фото из списка в словаре по индексу.
            Поиск осуществляется по ID юзера
        zero_list:
            Нужен для обнуления списка в словаре по ID юзера
    """
    def __init__(self,
                 hotelId: str,
                 call: telebot.types.CallbackQuery,
                 bot: telebot.TeleBot,
                 rapid_token: str,
                 url: str,
                 head_ers: dict
                 ):
        self.hotelId: str = hotelId
        self.call: telebot.types.CallbackQuery = call
        self.bot: telebot.TeleBot = bot
        self.rapid_token: str = rapid_token
        self.url: str = url
        self.foto_dict_url: dict = dict()
        self.data: Optional = None
        self.headers: dict = head_ers

    def get_foto(self):
        querystring: dict = {"id": self.hotelId}
        try:
            response: requests = requests.request("GET", self.url, headers=self.headers, params=querystring)
            data: json = json.loads(response.text)
            self.data: json = data
            self.foto_dict_url[self.call.message.chat.id]: list = []
            for index in range(len(data["hotelImages"])):
                size_foto: str = data["hotelImages"][index]["sizes"][0]['suffix']
                img: str = re.sub(r'{size}', size_foto, data["hotelImages"][index]["baseUrl"])
                if validators.url(img):
                    self.foto_dict_url[self.call.message.chat.id].append(img)
            self.pag_foto(page=1)
        except Exception:
            logger.exception('Ошибка при выводе фото')
            return Exception

    def pag_foto(self, page: int):
        try:
            paginator: InlineKeyboardPaginator = InlineKeyboardPaginator(
                len(self.foto_dict_url[self.call.message.chat.id]) - 1,
                current_page=page,
                data_pattern='elements#{page}'
            )
            paginator.add_after(telebot.types.InlineKeyboardButton(
                'Закрыть просмотр фоток',
                callback_data='back_all_foto'
            ))

            self.bot.send_photo(
                self.call.message.chat.id,
                self.foto_dict_url[self.call.message.chat.id][page - 1],
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
        except Exception:
            logger.exception('Ошибка пагинации фото')
            self.foto_dict_url[self.call.message.chat.id].pop(page - 1)
            self.pag_foto(page)

    def zero_list(self, msg: telebot.types.Message):
        try:
            if msg.chat.id in self.foto_dict_url:
                self.foto_dict_url[msg.chat.id]: list = []
        except Exception:
            return Exception
