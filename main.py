import telebot
import requests
import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv('API_KEY')

# Логирование
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('WARNING.log')],
)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('ERROR.log')],
)

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('CRITICAL.log')],
)

bot = telebot.TeleBot(TOKEN)
API = API_KEY

# Отслеживание команды старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, какой город хочешь глянуть?')

# Функция, когда пользователь вводит текст
@bot.message_handler(content_types=['text'])
def weather(message):
    city = message.text.strip().lower()

    try:
        # Отправка запроса к API
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
        res.raise_for_status()  # Проверяем на ошибку HTTP
        data = res.json()  # Преобразуем ответ в формат JSON

        temp = data['main']['temp']
        cloudiness = data['clouds']['all']
        wind_speed = data['wind']['speed']
        feels_like = data["main"]["feels_like"]

        rain = "rain" in data and data["rain"]
        snow = "snow" in data and data["snow"]

        if rain:
            precipitation = "🌧 Идёт дождь"
        elif snow:
            precipitation = "❄ Идёт снег"
        else:
            precipitation = "☀ Осадков нет"

        bot.reply_to(message, f'\nтемпература воздуха {temp}\u00B0C \nощущается как {feels_like}\u00B0C \nоблачность {cloudiness}% \nскорость ветра: {wind_speed} м/с \n\n{precipitation}')

        # выбор картинки по результатам
        if feels_like > 26.0 and not rain and not snow:
            image = 'heat.jpg'
        elif 12.0 < feels_like <= 26.0 and not rain and not snow:
            image = 'warm.jpg'
        elif 5.0 < feels_like <= 12.0 and not rain and not snow:
            image = 'chilly.jpg'
        elif -3.0 < feels_like <= 5.0 and not rain and not snow:
            image = 'cold.jpg'
        elif feels_like <= -3.0 and not rain and not snow:
            image = 'very_cold.jpg'
        elif -100.0 < feels_like < 100.0 and rain and not snow:
            image = 'rain.jpg'
        elif feels_like < 0 and not rain and snow:
            image = 'snowfall.jpg'
        else:
            image = 'unknown.jpg'
        # обработка ошибок с изображениями
        try:
            # Открытие файла и отправка изображения
            with open(f'./{image}', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        except FileNotFoundError:
            logging.error(f"Ошибка: файл {image} не найден.")
            bot.reply_to(message, 'Не удалось найти изображение для этой погоды.')
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")
            bot.reply_to(message, 'Произошла ошибка при отправке изображения.')

    except requests.exceptions.RequestException as e:
        # Ошибка при запросе
        logging.error(f"Ошибка при запросе данных для города {city}: {e}")
        bot.reply_to(message, 'Не удалось получить данные о погоде.')
    except ValueError as e:
        # Ошибка при обработке JSON
        logging.error(f"Ошибка при парсинге данных для города {city}: {e}")
        bot.reply_to(message, 'Не удалось обработать данные о погоде.')
    except Exception as e:
        # Обработка всех прочих ошибок
        logging.error(f"Неизвестная ошибка при обработке запроса от пользователя {message.chat.id}: {e}")
        bot.reply_to(message, 'Произошла ошибка, попробуй позже.')

bot.polling(none_stop=True)
