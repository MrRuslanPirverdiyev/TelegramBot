import requests
import json
from loguru import logger


class Location:
    """
    Класс Location: Нужен для поиска города,возвращает ID города
    Принимает данные:
        rapid_api_token,
        url,
        head_ers
    """
    def __init__(self, rapid_api_token: str, url: str, head_ers: dict):
        self.rapid_api_token: str = rapid_api_token
        self.url: str = url
        self.headers: dict = head_ers

    def loc_id(self, user_msg: str):
        querystring: dict = {"query": user_msg, "locale": "ru_RU", "currency": "USD"}
        try:
            response: requests = requests.request("GET", self.url, headers=self.headers, params=querystring)
            data_id: json = json.loads(response.text)
            if len(data_id["suggestions"]) > 0:
                return data_id["suggestions"][0]["entities"][0]["destinationId"]
            else:
                return None
        except Exception:
            logger.exception('Сбой при поиске города')
            return Exception
