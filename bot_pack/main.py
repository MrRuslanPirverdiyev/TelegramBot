import telebot
import os
import re
import botrequests.states
from loguru import logger
from typing import Optional
from datetime import datetime, date
from dotenv import load_dotenv
from botrequests.user_chat_log import UserManager
from botrequests.lowprice import Lowprice
from botrequests.hightprice import Hightprice
from botrequests.bestdeal import Bestdeal
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


class Main:
    """
    Класс Main: Является основным,где идет обработка команд и запросов юзера.
    В основном содержит хендлеры телеграмбот
    """

    def __init__(self, bot, data, low, hight, best):
        self.bot: telebot.TeleBot = bot
        self.data: UserManager = data
        self.low: Lowprice = low
        self.hight: Hightprice = hight
        self.best: Bestdeal = best
        self.check_in: Optional = None
        self.check_out: Optional = None
        self.msg: Optional = None
        logger.add('log_us.log', backtrace=True, diagnose=True, rotation='20 MB')

        @self.bot.callback_query_handler(func=lambda call: call.data == '/lowprice')
        def call_low(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.data_sending(
                identity=call.message.chat.id,
                name=call.message.chat.first_name,
                nick=call.message.chat.username,
                text=call.data
            )
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.bot.send_message(call.message.chat.id, "Отлично,укажите город для поиска")
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOWPRICE.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/highprice')
        def call_hight(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.data_sending(
                identity=call.message.chat.id,
                name=call.message.chat.first_name,
                nick=call.message.chat.username,
                text=call.data
            )
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.bot.send_message(call.message.chat.id, "Отлично,укажите город для поиска")
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHPRICE.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/bestdeal')
        def call_best(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.data_sending(
                identity=call.message.chat.id,
                name=call.message.chat.first_name,
                nick=call.message.chat.username,
                text=call.data
            )
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.bot.send_message(call.message.chat.id, "Отлично,укажите город для поиска")
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_BESTDEAL.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/history')
        def call_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.data_sending(
                identity=call.message.chat.id,
                name=call.message.chat.first_name,
                nick=call.message.chat.username,
                text=call.data
            )
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_RUN.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
                keyboard.add(telebot.types.InlineKeyboardButton(text='Lowprice', callback_data='/lowprice_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Hightprice', callback_data='/highprice_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Bestdeal', callback_data='/bestdeal_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Закрыть просмотр истории',
                                                                callback_data='/exit_looking_hist#'))
                self.bot.send_message(
                    call.message.chat.id,
                    text='{}'.format(
                        'Нажмите на один из вариантов'
                    ),
                    reply_markup=keyboard
                )
            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HISTORY.value:
                keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
                keyboard.add(telebot.types.InlineKeyboardButton(text='Lowprice', callback_data='/lowprice_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Hightprice', callback_data='/highprice_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Bestdeal', callback_data='/bestdeal_hist_in_data'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Закрыть просмотр истории',
                                                                callback_data='/exit_looking_hist#'))
                self.bot.send_message(
                    call.message.chat.id,
                    text='{}'.format(
                        'Нажмите на один из вариантов'
                    ),
                    reply_markup=keyboard
                )
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_HISTORY.value)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('hotels#'))
        def call_hotels(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.low.pag_hotels_low(call.data[7:])
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOW_FINDOTEL.value)

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.hight.pag_hotels_hight(call.data[7:])
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHT_FINDOTEL.value)

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.best.pag_hotels_best(call.data[7:])
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_BEST_FINDOTEL.value)

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FOTOOTEL.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FOTOOTEL.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FOTOOTEL.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_GOOGLEMAP.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_GOOGLEMAP.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_GOOGLEMAP.value:
                self.bot.answer_callback_query(call.id, 'Закройте последний запрос')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('elements#'))
        def call_get_foto_hotel(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.low.pag(call.data[9:])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.hight.pag(call.data[9:])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.best.pag(call.data[9:])

        @self.bot.callback_query_handler(func=lambda call: call.data.strip('[]').split(',')[0] == '/foto_gallery')
        def call_foto(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOW_FOTOOTEL.value)
                self.low.find_fotos(call, self.bot, call.data.strip('[]').split(',')[1])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHT_FOTOOTEL.value)
                self.hight.find_fotos(call, self.bot, call.data.strip('[]').split(',')[1])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_BEST_FOTOOTEL.value)
                self.best.find_fotos(call, self.bot, call.data.strip('[]').split(',')[1])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_GOOGLEMAP.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_GOOGLEMAP.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_GOOGLEMAP.value:
                self.bot.answer_callback_query(call.id, 'Закройте карту')

        @self.bot.callback_query_handler(func=lambda call: call.data.strip('[]').split(',')[0] == '/google_map_holel')
        def call_map(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOW_GOOGLEMAP.value)
                self.low.loc_start(call.data.strip('[]').split(',')[1], call.data.strip('[]').split(',')[2])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHT_GOOGLEMAP.value)
                self.hight.loc_start(call.data.strip('[]').split(',')[1], call.data.strip('[]').split(',')[2])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_BEST_GOOGLEMAP.value)
                self.best.loc_start(call.data.strip('[]').split(',')[1], call.data.strip('[]').split(',')[2])

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FOTOOTEL.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FOTOOTEL.value or \
                    self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FOTOOTEL.value:
                self.bot.answer_callback_query(call.id, 'Закройте просмотр фото')

        @self.bot.callback_query_handler(func=lambda call: call.data == 'back_all_foto')
        def call_back_foto(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOW_FINDOTEL.value)
                self.low.list_back_fotos()

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHT_FINDOTEL.value)
                self.hight.list_back_fotos()

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FOTOOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_BEST_FINDOTEL.value)
                self.best.list_back_fotos()

        @self.bot.callback_query_handler(func=lambda call: call.data == 'back_find_hotels')
        def call_back_find_hotels(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)
                self.low.list_back_hotels()

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)
                self.hight.list_back_hotels()

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)
                self.best.list_back_hotels()

            else:
                self.bot.answer_callback_query(call.id, 'Закройте пред_ий запрос')

        @self.bot.callback_query_handler(func=lambda call: call.data == '/close_map_location')
        def call_back_close_map(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_GOOGLEMAP.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_LOW_FINDOTEL.value)

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_GOOGLEMAP.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_HIGHT_FINDOTEL.value)

            elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_GOOGLEMAP.value:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_BEST_FINDOTEL.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'exit_city_find#')
        def exit_all(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/back_page_log_chat#')
        def exit_all(call: telebot.types.CallbackQuery):
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/lowprice_hist_in_data')
        def low_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            hisoty_count: list = re.findall(r'\w+',
                                            str(list(i for i in self.data.low_price_hist_out(call.message.chat.id))
                                                ))
            if len(hisoty_count) > 0:
                self.bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
                keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
                keyboard.add(
                    telebot.types.InlineKeyboardButton(
                        text='Закрыть список',
                        callback_data='exit_in_list_hist#'
                    ))
                self.bot.send_message(
                    call.message.chat.id,
                    self.data.low_price_hist_out(call.message.chat.id),
                    reply_markup=keyboard
                )
            else:
                self.bot.answer_callback_query(call.id, 'Список пуст')

        @self.bot.callback_query_handler(func=lambda call: call.data == '/highprice_hist_in_data')
        def hight_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            hisoty_count: list = re.findall(r'\w+',
                                            str(list(i for i in self.data.hight_price_hist_out(call.message.chat.id))
                                                ))
            if len(hisoty_count) > 0:
                self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
                keyboard.add(
                    telebot.types.InlineKeyboardButton(
                        text='Закрыть список',
                        callback_data='exit_in_list_hist#'
                    ))
                self.bot.send_message(
                    call.message.chat.id,
                    self.data.hight_price_hist_out(call.message.chat.id),
                    reply_markup=keyboard
                )
            else:
                self.bot.answer_callback_query(call.id, 'Список пуст')

        @self.bot.callback_query_handler(func=lambda call: call.data == '/bestdeal_hist_in_data')
        def hight_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            hisoty_count: list = re.findall(r'\w+',
                                            str(list(i for i in self.data.bestdeal_hist_out(call.message.chat.id))
                                                ))
            if len(hisoty_count) > 0:
                self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text='Закрыть список',
                    callback_data='exit_in_list_hist#'
                ))
                self.bot.send_message(
                    call.message.chat.id,
                    self.data.bestdeal_hist_out(call.message.chat.id),
                    reply_markup=keyboard
                )
            else:
                self.bot.answer_callback_query(call.id, 'Список пуст')

        @self.bot.callback_query_handler(func=lambda call: call.data == 'exit_in_list_hist#')
        def exit_list_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_HISTORY.value)
            call_hist(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == '/exit_looking_hist#')
        def exit_look_hist(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            self.bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
            self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('cbcal_1_'))
        def call_calendar_in(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            step_key: dict = {'month': 'месяц', 'day': 'день', 'year': 'год'}
            result_in, key_in, step_in = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(call.data)
            if not result_in and key_in:
                self.bot.edit_message_text(f'Дата заезда: {step_key[LSTEP[step_in]]}',
                                           call.message.chat.id,
                                           call.message.message_id,
                                           reply_markup=key_in)
            elif result_in:
                self.check_in = result_in
                self.bot.edit_message_text(f'Выбрано {result_in} на дату заезда',
                                           call.message.chat.id,
                                           call.message.message_id,
                                           reply_markup=key_in)
                if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                    self.low.calendar_call_out()
                elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                    self.hight.calendar_call_out()
                elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                    self.best.calendar_call_out()
            elif call.data == 'cbcal_1_n':
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('cbcal_2_'))
        def call_calendar_out(call: telebot.types.CallbackQuery):
            logger.debug(f'| Пользователь {call.message.chat.id} | Выбрал команду {call.data} |')
            step_key: dict = {'month': 'месяц', 'day': 'день', 'year': 'год'}
            result_out, key_out, step_out = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).process(call.data)
            if not result_out and key_out:

                self.bot.edit_message_text(f'Дата выезда: {step_key[LSTEP[step_out]]}',
                                           call.message.chat.id,
                                           call.message.message_id,
                                           reply_markup=key_out)
            elif result_out:
                self.check_out = result_out
                self.bot.edit_message_text(f'Выбрано {result_out} на дату выезда',
                                           call.message.chat.id,
                                           call.message.message_id,
                                           reply_markup=key_out)
                if self.data.get_states(call.message.chat.id) == botrequests.states.States.S_LOW_FINDOTEL.value:
                    self.low.results(self.check_in, self.check_out)
                elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_HIGHT_FINDOTEL.value:
                    self.hight.results(self.check_in, self.check_out)
                elif self.data.get_states(call.message.chat.id) == botrequests.states.States.S_BEST_FINDOTEL.value:
                    self.best.results(self.check_in, self.check_out)
            elif call.data == 'cbcal_2_n':
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
                self.data.states_write(call.message.chat.id, botrequests.states.States.S_RESTART.value)

        @self.bot.message_handler(commands=['start'])
        def get_text_messages(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Выбрал команду {message.text} |')
            self.data_sending(
                identity=message.from_user.id,
                name=message.from_user.first_name,
                nick=message.from_user.username,
                text=message.text
            )
            state: str = self.data.get_states(message.chat.id)
            if state == botrequests.states.States.S_LOW_FINDOTEL.value or \
                    state == botrequests.states.States.S_HIGHT_FINDOTEL.value or \
                    state == botrequests.states.States.S_BEST_FINDOTEL.value:
                self.bot.send_message(message.chat.id, "Закройте поиск отелей,либо нажмите /reset")
            elif state == botrequests.states.States.S_LOWPRICE.value or \
                    state == botrequests.states.States.S_HIGHPRICE.value or \
                    state == botrequests.states.States.S_BESTDEAL.value:
                self.bot.send_message(message.chat.id, "Кажется, вы не отправили мне город для поиска :( Жду...,либо нажмите /reset")
            elif state == botrequests.states.States.S_RUN.value:
                self.bot.send_message(message.chat.id, "Сделайте выбор либо закройте :( Жду...")
            elif state == botrequests.states.States.S_HISTORY.value:
                self.bot.send_message(message.chat.id, "Спрева закройте список истории,либо нажмите /reset")
            elif state == botrequests.states.States.S_LOW_FOTOOTEL.value or \
                    state == botrequests.states.States.S_HIGHT_FOTOOTEL.value or \
                    state == botrequests.states.States.S_BEST_FOTOOTEL.value:
                self.bot.send_message(message.chat.id, "Закройте просмотр фото,либо нажмите /reset")
            elif state == botrequests.states.States.S_LOW_GOOGLEMAP.value or \
                    state == botrequests.states.States.S_HIGHT_GOOGLEMAP.value or \
                    state == botrequests.states.States.S_BEST_GOOGLEMAP.value:
                self.bot.send_message(message.chat.id, "Закройте карту,либо нажмите /reset")
            elif state == botrequests.states.States.S_RESTART.value:
                self.data.states_write(message.chat.id, botrequests.states.States.S_RUN.value)
                user_entering_name_com(message)
            else:
                self.bot.send_message(message.chat.id, 'Привет, рад приветствовать вас,как вас зовут?')
                self.data.states_write(message.chat.id, botrequests.states.States.S_RUN.value)

        @self.bot.message_handler(commands=["reset"])
        def cmd_reset(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Выбрал команду {message.text} |')
            self.data.states_write(message.chat.id, botrequests.states.States.S_FICCHA.value)
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = telebot.types.KeyboardButton('/Да')
            btn_2 = telebot.types.KeyboardButton('/Нет')
            markup.add(btn_1, btn_2)
            self.bot.send_message(message.chat.id, "Что ж, начнём по-новой?", reply_markup=markup)

        @self.bot.message_handler(commands=["Да"])
        def reset_positiv(message: telebot.types.Message):
            if self.data.get_states(message.chat.id) == botrequests.states.States.S_FICCHA.value:
                logger.debug(f'| Пользователь {message.chat.id} | Выбрал команду {message.text} |')
                self.low.list_back_hotels()
                self.hight.list_back_hotels()
                self.best.list_back_hotels()
                self.low.list_back_fotos()
                self.hight.list_back_fotos()
                self.best.list_back_fotos()
                self.data.states_write(message.chat.id, botrequests.states.States.S_RUN.value)
                user_entering_name_com(message)

        @self.bot.message_handler(commands=["Нет"])
        def reset_negativ(message: telebot.types.Message):
            if self.data.get_states(message.chat.id) == botrequests.states.States.S_FICCHA.value:
                logger.debug(f'| Пользователь {message.chat.id} | Выбрал команду {message.text} |')
                self.low.list_back_hotels()
                self.hight.list_back_hotels()
                self.best.list_back_hotels()
                self.low.list_back_fotos()
                self.hight.list_back_fotos()
                self.best.list_back_fotos()
                self.data.states_write(message.chat.id, botrequests.states.States.S_RESTART.value)
                markup_1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn = telebot.types.KeyboardButton('/start')
                markup_1.add(btn)
                self.bot.send_message(message.chat.id, "Ясно(", reply_markup=markup_1)

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(message.chat.id) == botrequests.states.States.S_RUN.value)
        def user_entering_name_com(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Выбирает варианты поиска |')
            self.data_sending(
                identity=message.from_user.id,
                name=message.from_user.first_name,
                nick=message.from_user.username,
                text=message.text
            )
            keyboard: telebot.types.InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Отели по низким ценам', callback_data='/lowprice'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Отели по высоким ценам', callback_data='/highprice'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Лучшие предложения', callback_data='/bestdeal'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='История поиска', callback_data='/history'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Выйти из поиска', callback_data='exit_city_find#'))
            self.bot.send_message(
                message.from_user.id,
                text='{}'.format(
                    'Поиск будет произведен по этим данным'
                ),
                reply_markup=keyboard
            )

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(message.chat.id) == botrequests.states.States.S_LOWPRICE.value)
        def user_entering_hotel_name_low(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Ищет отели по убыванию |')
            self.low.find_hotels(message, self.bot, self.data)
            self.data.states_write(message.chat.id, botrequests.states.States.S_LOW_FINDOTEL.value)

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(message.chat.id) == botrequests.states.States.S_HIGHPRICE.value)
        def user_entering_hotel_name_hight(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Ищет отели по возрастанию |')
            self.hight.find_hotels(message, self.bot, self.data)
            self.data.states_write(message.chat.id, botrequests.states.States.S_HIGHT_FINDOTEL.value)

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(message.chat.id) == botrequests.states.States.S_BESTDEAL.value)
        def user_entering_hotel_name_best(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Ищет отели по выбору |')
            self.msg = message
            self.data_sending(
                identity=message.from_user.id,
                name=message.from_user.first_name,
                nick=message.from_user.username,
                text=message.text
            )
            bot.send_message(message.chat.id, 'Укажите диапазон цен через пробел,вылюта - USD')
            self.data.states_write(message.chat.id, botrequests.states.States.S_BESTDEAL_PRICE.value)

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(
                message.chat.id) == botrequests.states.States.S_BESTDEAL_PRICE.value)
        def user_entering_hotel_name_best(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Задает цену |')
            self.data_sending(
                identity=message.from_user.id,
                name=message.from_user.first_name,
                nick=message.from_user.username,
                text=message.text
            )
            bot.send_message(message.chat.id, 'Укажите расстояние в км через пробел')
            self.data.states_write(message.chat.id, botrequests.states.States.S_BESTDEAL_DIS.value)

        @self.bot.message_handler(
            func=lambda message: self.data.get_states(
                message.chat.id) == botrequests.states.States.S_BESTDEAL_DIS.value)
        def user_entering_hotel_name_best(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Задает дистанцию |')
            self.msg = message
            self.data_sending(
                identity=message.from_user.id,
                name=message.from_user.first_name,
                nick=message.from_user.username,
                text=message.text
            )
            self.best.find_hotels(message, self.bot, self.data)
            self.data.states_write(message.chat.id, botrequests.states.States.S_BEST_FINDOTEL.value)

        @self.bot.message_handler(commands=["help"])
        def help_hen(message: telebot.types.Message):
            logger.debug(f'| Пользователь {message.chat.id} | Выбрал команду {message.text} |')
            text: str = '{} \n{} \n{} \n{} \n{} \n{}'.format(
                '/start - для начала работы с ботом',
                '/reset - перезапуск бота',
                'Истрия поиска - Выводит вашу историю',
                'Отели по низким ценам - Начинает поиск по мин ценам',
                'Отели по высоким ценам - Начинает поиск по макс ценам',
                'Лучшие предложения - Начинает поиск по вашиму выбору'
            )
            self.bot.send_message(message.chat.id, text)
            self.data.states_write(message.chat.id, botrequests.states.States.S_HELP.value)

    def data_sending(self, identity: int, name: str, nick: str, text: str):
        time_real = datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
        logger.debug(f'| Записываются данные пользователя {identity} |')
        if text in '/start':
            new_text: str = '{} {}'.format(
                'Пользователь запустил бота',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)
        elif text == '/lowprice':
            new_text: str = '{} {}'.format(
                'Пользователь выбрал поиск по мин ценам',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)

        elif text == '/higtprice':
            new_text: str = '{} {}'.format(
                'Пользователь выбрал поиск по макс ценам',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)

        elif text == '/bestdeal':
            new_text: str = '{} {}'.format(
                'Пользователь выбрал кастомный поиск',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)
        elif text == '/history':
            new_text: str = '{} {}'.format(
                'Пользователь посмотрел чат-историю',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)

        elif text == '/run':
            new_text: str = '{} {}'.format(
                'Пользователь запустил варианты поиска',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)

        elif self.msg is not None:
            if self.data.get_states(self.msg.chat.id) == botrequests.states.States.S_BESTDEAL.value or \
                    self.data.get_states(self.msg.chat.id) == botrequests.states.States.S_BESTDEAL_PRICE.value or \
                    self.data.get_states(self.msg.chat.id) == botrequests.states.States.S_BESTDEAL_DIS.value:
                self.data.bestdeal_loc_pr_dis_base(identity, text)

        else:
            new_text = '{} {}'.format(
                'Пользователь написал',
                text
            )
            self.data.db_table_val(user_id=identity, user_name=name, nick_name=nick, log_text=new_text, tme=time_real)

    def run(self):
        self.bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    load_dotenv()
    runnig = Main(
        bot=telebot.TeleBot(os.getenv('SECRET_TOKEN')),
        data=UserManager(),
        low=Lowprice(),
        hight=Hightprice(),
        best=Bestdeal()
    )
    runnig.run()
