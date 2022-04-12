import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

"""Настройка логов."""
logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Кастомная ошибка API."""

    pass


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Отправлено сообщение: "{message}"')
    except Exception as error:
        logger.error(f'Cбой отправки сообщения, ошибка: {error}')


def get_api_answer(current_timestamp):
    """Запрос к API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        message = 'Ошибка при вызове API'
        logger.error(message)
        raise APIError(message)
    try:
        if response.status_code != HTTPStatus.OK:
            message = 'API не отвечает'
            logger.error(message)
            raise Exception(message)
    except Exception:
        message = 'Ошибка при вызове API'
        logger.error(message)
        raise APIError(message)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        message = 'Ответ API не словарь'
        logger.error(message)
        raise TypeError(message)
    if ['homeworks'][0] not in response:
        message = 'В ответе API нет домашней работы'
        logger.error(message)
        raise IndexError(message)
    homework = response.get('homeworks')[0]
    return homework


def parse_status(homework):
    """Извлечение из информации о конкретной домашней работе."""
    keys = ['status', 'homework_name']
    for key in keys:
        if key not in homework:
            message = f'Ключа {key} нет в ответе API'
            logger.error(message)
            raise KeyError(message)
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Неизвестный статус домашней работы'
        logger.error(message)
        raise KeyError(message)
    homework_name = homework['homework_name']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет переменные окружения."""
    vars = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return None not in vars


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 86400)
    if check_tokens is False:
        message = 'Проблема с переменными окружения'
        logger.critical(message)
        raise SystemExit(message)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if 'current_date' in response:
                current_timestamp = response['current_date']
            homework = check_response(response)
            if homework is not None:
                message = parse_status(homework)
                if message is not None:
                    send_message(bot, message)
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'

            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
