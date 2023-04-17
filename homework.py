import logging
import os
import sys
import time
import requests
import telegram
from http import HTTPStatus
from dotenv import load_dotenv
from exceptions import (
    DotEnvError,
    EndpointUnreachableError,
    UnknownHWStatus,
    NoneEnvValueError,
)
from telegram.error import TelegramError
from requests.exceptions import RequestException

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, [%(levelname)s], %(message)s, %(name)s',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверка наличие всех переменных окружения."""
    if not all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        massage = ('Отсутствуют переменные окружения.')
        logging.critical(massage)
        raise NoneEnvValueError(massage)
    return True


def send_message(bot, message):
    """Отправляет сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Удачно отправлено сообщение.')
    except TelegramError:
        logging.error('Сообщение не отправлено.')


def get_api_answer(timestamp):
    """Получение ответа от API."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise UnknownHWStatus('Некорректный статус ответа от API')
        return homework_statuses.json()
    except RequestException as error:
        logging.error(f'Непредвиденная ошибка обращения к API: {error}')
        raise EndpointUnreachableError('Ошибка при обращении к API')


def check_response(response):
    """Проверка ответа API на соответствие типам данных."""
    logging.debug(response)
    if not isinstance(response, dict):
        raise TypeError('Переменная не является словарём.')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Не является списком.')
    return True


def parse_status(homework):
    """Извлечение статуса домашней работы."""
    if homework['status'] not in HOMEWORK_VERDICTS:
        logging.error(f'Неизвестный статус - {homework["status"]}')
        raise UnknownHWStatus('Неизвестный статус домашней работы.')
    if not homework.get('homework_name'):
        logging.error('В ответе нет ключа "homework_name".')
        raise ValueError('Нет статуса домашней работы.')
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise DotEnvError('Нет одной или нескольких переменных окружения.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_status = str()
    last_error = str()

    while True:
        try:
            answer = get_api_answer(timestamp - 30 * 86400)
            if not check_response(answer):
                logging.error('Ответ API некорректный')
                raise TypeError('Ответ API некорректный')
            else:
                homework = answer['homeworks'][0]

            if homework['status'] != last_status:
                last_status = homework['status']
                send_message(bot, parse_status(homework))
                logging.debug(f'Отправлено сообщение {parse_status(homework)}')
            else:
                logging.debug('Статус домашнего задания не изменился')
        except Exception as error:
            print(Exception)
            message = f'Сбой в работе программы: {error}'
            if str(error) != last_error:
                send_message(bot, message)
                last_error = str(error)
            logging.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
