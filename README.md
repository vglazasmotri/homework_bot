<h1 align=center>🌟Telegram-бот ассистент🌟</h1>

## 📄 **Описание**

Telegram-бот, который обращатся к API сервиса Практикум.Домашка и узнает статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

<br>
<br>

## 🛠️ Инструкция по установке

Клонируйте репозиторий:

```
git clone git@github.com:vglazasmotri/telegram_bot.git
```

```
cd telegram_bot
```

Устанавливаем виртуальное окружение:

```
python -m venv venv
```

Активируем виртуальное окружение:
```
source venv/Scripts/activate
```

Обновляем Pip:
```
python -m pip install --upgrade pip
```
Устанавливаем зависимости:
```
pip install -r requirements.txt
```

Создать файл виртуального окружения ```.env``` в корневой директории проекта:
```bash
touch .env
```
В созданном ```.env``` файле прописать токены в следующем формате:
* токен API сервиса Практикум.Домашка
```
echo PRACTICUM_TOKEN=************** >> .env
```
* токен Bot API Telegram для отправки уведомлений
```
echo TELEGRAM_TOKEN=************* >> .env
```
* ID Telegram чата для получения уведомлений
```
echo CHAT_ID=**************** >> .env
```
5. Запустить проект на локальной машине:
```
python homework.py
```

Готово!


<br>
<br>

## 🛠️ Применяемые технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- Python 3.7
- Python-telegram-bot 13.7


## 💪 Автор:

- Сергей Сыч Python-разработчик (https://github.com/vglazasmotri)
