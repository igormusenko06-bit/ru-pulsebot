import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8655371651:AAGrecLlCakLa7Pcv5JTG94BPpiRFw4qbQc"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Бот работает ✅")

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
