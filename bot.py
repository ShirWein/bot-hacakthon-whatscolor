import logging
from color_extraction import extract_color
from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    Updater, MessageHandler, Filters,
)
from key import api

WELCOME_TEXT = "Welcome to 🤖🎨👁️ What's color bot! 🤖🎨👁️"

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

def receive_image(update, context):
    image = update.message.photo[-1].get_file()
    print(image)
    update.message.reply_text('Just a moment I am scanning the image ---->')
    result = extract_color(image['file_path'])
    print(result)
    update.message.reply_text(result)

# def error(update, context):
#     update.message.reply_text(f"Wrong input, please send an image")

# ----------------- STARTING THE BOT ---------------------
logger.info("Starting up bot...")
updater = Updater(api, use_context=True)
dp = updater.dispatcher

# Commands
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(MessageHandler(Filters.all, receive_image))
# dp.add_handler(MessageHandler(Filters.all, error))

# Errors
# dp.add_error_handler(error)

# Run the bot
updater.start_polling()
updater.idle()
logger.info("Bye!")
