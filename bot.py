import logging
import time
from threading import Thread

from color_extraction import extract_color
from telegram import *
from telegram.ext import *
from key import api

WELCOME_TEXT = """Welcome to WhatsColor bot!\nTo use this bot please make sure:\n1. Take a photo with the flash on 🔦\n2. Try to isolate the object in the photo\n3. Multi-color object might be inaccurate"""

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# the start command
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT)

# the /help command
def help_command(update, context):
    update.message.reply_text('You need to upload an image, I will scan it and return the dominant color in that image.')

counter = 0
def receive_image(update, context):
    global counter
    counter += 1
    image = update.message.photo[-1].get_file()
    logger.info(f"recived image:#{counter} {image}")
    update.message.reply_text('Just a moment I am scanning the image ---->')
    Thread(target=process_image, args=(context, counter, image, update)).start()


def process_image(context, counter, image, update):
    t0 = time.perf_counter()
    result = extract_color(image['file_path'])
    t = time.perf_counter() - t0
    logger.info(f"result for image:{counter} {result[0]} time={t:.1f}")
    update.message.reply_text(result[0])
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=result[1])
    logger.info(f"sent image:{counter}")


# ----------------- STARTING THE BOT ---------------------
logger.info("Starting up bot...")
updater = Updater(api, use_context=True)
dp = updater.dispatcher

# Commands
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(MessageHandler(Filters.all, receive_image))
# dp.add_handler(MessageHandler(Filters.all, error))

# Run the bot
updater.start_polling()
updater.idle()
logger.info("Bye!")
