# homework-bot
Чат-бот Telegram для получения информации о проведенном код-ревью домашнего задания (Telegram API)

Проект выполнен в рамках учебного курса Яндекс.Практикум.

Проект размещен на Heroku.
___________________________________________________
Программа написана на Python с использованием:
- requests (направление http-запроса на сервер),
- python-dotenv (загрузка и считывание переменных окружения из файла .env)
- python-telegram-bot (работа с Телеграм-ботом)

## Как работает программа:
Чат-бот Телеграм обращается к API, которое возвращает изменение статуса домашнего задания и сообщает проверено ли задание, провалено или принято.

## Как запустить программу:

1) В директории проекта установите виртуальное окружение, активируйте его и установите необходимые зависимости:
```
python -m venv venv

source venv/Scripts/activate 

pip install -r requirements.txt
```
2) Создайте чат-бота Телеграм
3) Создайте в директории файл .env и поместите туда необходимые токены в формате PRAKTIKUM_TOKEN = 'ххххххххх', TELEGRAM_TOKEN = 'ххххххххххх',
TELEGRAM_CHAT_ID = 'ххххххххххх'
4) Откройте файл homework.py и запустите код




### Пример ответа чат-бота:
{
   "homeworks":[
      {
         "id":123,
         "status":"approved",
         "homework_name":"username__hw_python_oop.zip",
         "reviewer_comment":"Работа проверена: ревьюеру всё понравилось. Ура!",
         "date_updated":"2020-02-13T14:40:57Z",
         "lesson_name":"Итоговый проект"
      }
   ],
   "current_date":1581604970
}
