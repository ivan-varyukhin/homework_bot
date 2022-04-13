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
    logger.debug('Запрос к API...')
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            message = 'Ответ API отличен от ОК'
            logger.error(message)
            raise Exception(message)
    except Exception:
        message = 'Ошибка при вызове API'
        logger.error(message)
        raise APIError(message)
    try:
        data = response.json()
    except Exception:
        message = 'Ответ API не json'
        logger.error(message)
        raise ValueError(message)
    return data


def check_response(response):
    """Проверка ответа API на корректность."""
    logger.debug('Проверка ответа API на корректность...')
    if 'current_date' in response:
        global current_timestamp
        current_timestamp = response['current_date']
    homeworks = response['homeworks']
# так автотест не жрет
#    homeworks = response.get('homeworks')
    if homeworks is None:
        message = 'Список пуст'
        raise APIError(message)
    if not isinstance(homeworks, list):
        message = 'Неверный формат ответа'
        raise APIError(message)
    if not homeworks:
        return None

    homework = response.get('homeworks')[0]
    return homework


def parse_status(homework):
    """Извлечение из информации о конкретной домашней работе."""
    logger.debug('Получение данных о домашней работе...')
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
    logger.debug('Проверка переменных окружения...')
    vars = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(vars)


def main():
    """Основная логика работы бота."""
    logger.debug('Запуск...')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
#    current_timestamp = int(time.time() - 86400)
    current_timestamp = 0
    if check_tokens is False:
        message = 'Проблема с переменными окружения'
        logger.critical(message)
        raise SystemExit(message)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework is None:
                continue
            message = parse_status(homework)
            if message is None:
                continue
            send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(message)

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
