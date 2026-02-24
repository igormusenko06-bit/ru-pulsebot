import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Bot
from telegram.ext import Updater, CommandHandler

TOKEN = "8655371651:AAGrecLlCakLa7Pcv5JTG94BPpiRFw4qbQc"
CHANNEL_ID = -1003761925434

logging.basicConfig(level=logging.INFO)

# ---- HTTP сервер для Render ----
def start_http_server():
    port = int(os.environ.get("PORT", 10000))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, format, *args):
            return

    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=start_http_server, daemon=True).start()
# --------------------------------


def start(update, context):
    update.message.reply_text("Бот работает ✅")


def test_signal(update, context):
    bot = Bot(token=TOKEN)
    bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 ТЕСТ СИГНАЛ\n\nMOEX FUTURES\nBUY\nTP: 123.45\nSL: 120.00"
    )
    update.message.reply_text("Сигнал отправлен в канал ✅")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("signal", test_signal))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
