class EndpointUnreachableError(Exception):
    """Ошибка при обращении к API."""


class UnknownHWStatus(Exception):
    """Неизвестный статус домашней работы."""


class NoneEnvValueError(Exception):
    """Нет одной или нескольких переменных окружения."""
