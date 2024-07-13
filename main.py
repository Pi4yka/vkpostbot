import os, logging

from dotenv import load_dotenv
from health_ping import HealthPing
import telebot

from controllers import admin

# Загрузка переменных окружения из .env файла
load_dotenv()
    
# Получение токена бота из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
VK_TOKEN = os.getenv('VK_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
    

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    if (admin.checkAdmin(user_id)):
        bot.send_message(user_id, "Привет! Я бот 'Котов и Эмо', могу посмотреть предложку или предложить пост сам")
    else:
        bot.send_message(user_id, "Привет! Я бот 'Котов и Эмо', но ты незнакомый мне человек.")


# inline клавиатура
@bot.message_handler(commands=['help'])
def help_handler(message):
    markup = telebot.types.InlineKeyboardMarkup()
    show_suggestion_post = telebot.types.InlineKeyboardButton("Suggestion Posts", callback_data='show_suggestion_post')
    generate_post = telebot.types.InlineKeyboardButton("Generate Post", callback_data='generate_post')
    another = telebot.types.InlineKeyboardButton("Another", callback_data='another')
    markup.row(show_suggestion_post, generate_post)
    markup.row(another)
    bot.send_message(message.chat.id, "Выбери что ты хочешь сделать", reply_markup=markup)


# Обработчик команды сделать заметку
@bot.message_handler(commands=['show_suggestion_post'])
def show_suggestion_post(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Сформированные посты из предложки")
    # bot.register_next_step_handler(message, save_note)


# Обработчик команды сделать заметку
@bot.message_handler(commands=['generate_post'])
def generate_post(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Генерирую фото кота...")
    # bot.register_next_step_handler(message, save_note)


# Обработчик команды сделать заметку
@bot.message_handler(commands=['another'])
def another(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Когда нибудь тут что то будет")
    # bot.register_next_step_handler(message, save_note)

def main():
    """Run the bot."""
    bot.infinity_polling()

if __name__ == "__main__":
    main()