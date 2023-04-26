import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()
PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: int = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
DAYS_AGO: int = 30
SECONDS_IN_DAY: int = 86400
SECONDS_AGO: int = DAYS_AGO * SECONDS_IN_DAY

ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: str = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, [%(levelname)s], %(message)s, %(name)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def check_tokens() -> None:
    """Проверка наличие всех переменных окружения."""
    if not all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        massage = ('Нет одной или нескольких переменных окружения.')
        logging.critical(massage)
        raise exceptions.NoneEnvValueError(massage)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Бот отправил сообщение: {message}')
    except telegram.error.TelegramError:
        logging.error('Сообщение не отправлено.')


def get_api_answer(timestamp: int) -> dict:
    """Получение ответа от API."""
    payload = {'from_date': timestamp}
    try:
        hm_statuses = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        logger.info(f'Отправлен запрос к API Практикума. '
                    f'Код ответа API: {hm_statuses.status_code}')
    except requests.exceptions.RequestException as error:
        message = f'API недоступен, ошибка: {error}'
        logging.error(message)
        raise exceptions.EndpointUnreachableError(message)
    if hm_statuses.status_code != HTTPStatus.OK:
        raise exceptions.UnknownHWStatus('Некорректный статус ответа API')
    try:
        homework_json = hm_statuses.json()
    except Exception as error:
        message = f'Сбой при переводе в формат json: {error}'
        logger.error(message)
        raise exceptions.InvalidJSONTransform(message)
    return homework_json


def check_response(response: dict) -> None:
    """Проверка ответа API на соответствие типам данных."""
    logging.debug(f'Ответ API: {response}.')
    if not isinstance(response, dict):
        message = 'Некорректный ответ API: Отсутствует словарь с данными.'
        logging.error(message)
        raise TypeError(message)

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        message = 'Некорректный ответ API: Отсутствует список домашних работ.'
        logging.error(message)
        raise TypeError(message)


def parse_status(homework: dict) -> str:
    """Извлечение статуса домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        message = f'Ключ {error} не найден в информации о домашней работе'
        logger.error(message)
        raise KeyError(message)

    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
        logger.info('Сформировано сообщение о статусе ДЗ.')
    except KeyError as error:
        message = f'Неизвестный статус домашней работы: {error}'
        logger.error(message)
        raise exceptions.UnknownHWStatus(message)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    logging.info('Бот начинает работу.')
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_status = str()
    last_error = str()

    while True:
        try:
            answer = get_api_answer(timestamp - SECONDS_AGO)
            logging.debug(f'Ответ:{answer}:')
            check_response(answer)
            homework = answer['homeworks'][0]

            if homework['status'] != last_status:
                message = parse_status(homework)
                last_status = homework['status']
                send_message(bot, message)
                logging.debug(f'В телеграмм отправлен статус ДЗ: {message}')
            else:
                logging.debug('Статус домашнего задания не изменился')
        except (
            KeyError,
            TypeError,
            requests.exceptions.RequestException,
            exceptions.EndpointUnreachableError,
            exceptions.UnknownHWStatus,
            exceptions.InvalidJSONTransform,
            telegram.error.TelegramError,
        ) as error:
            message = f'Сбой в работе программы, ошибка - {error}'
            logging.error(message)
            if message != last_error:
                last_error = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
