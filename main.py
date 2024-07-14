import os, logging

from dotenv import load_dotenv
from health_ping import HealthPing
import telebot
import vk

from controllers import admin, generateData

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

APIVersionVk = 5.131
vkApi = vk.API(access_token=VK_TOKEN)
vkApi.auth() 
session_apiVk = vkApi.get_api(v=APIVersionVk)
bot = telebot.TeleBot(TELEGRAM_TOKEN)


# inline клавиатура
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if (admin.checkAdmin(user_id)):
        # bot.send_message(user_id, "Привет! Я бот 'Котов и Эмо', могу посмотреть предложку или предложить пост сам")

        keyboard = telebot.types.InlineKeyboardMarkup()
        btn_suggestion = telebot.types.InlineKeyboardButton(text="Предложка", callback_data='suggestion')
        btn_gen_post = telebot.types.InlineKeyboardButton(text="Создать пост", callback_data = 'generate_post')
        keyboard.add(btn_suggestion, btn_gen_post)
        bot.send_message(chat_id,
                        'Привет! Я бот "Котов и Емо", могу посмотреть предложку или предложить пост сам',
                        reply_markup=keyboard)
    else:
        bot.send_message(user_id, "Привет! Я бот 'Котов и Эмо', но ты незнакомый мне человек.\nПодписывайся на наш паблик: https://vk.com/emomew")


@bot.callback_query_handler(func=lambda call: call.data == 'suggestion')
def suggestion_post(call):
    message = call.message
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Предложенные посты в паблике:')


@bot.callback_query_handler(func=lambda call: call.data == 'generate_post')
def suggestion_post(call):
    message = call.message
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Сгенерируем пост для паблика')
    # genPost = generateData.generatePost.generateImg()
    # bot.send_photo(chat_id, genPost)
    session_apiVk.wall.post(from_group=1, message="TESTPOST", v=APIVersionVk)
    bot.send_message(chat_id, f'post is publicaed!')
    

def main():
    """Run the bot."""
    bot.infinity_polling()

if __name__ == "__main__":
    main()