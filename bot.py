import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Bot
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ru-pulsebot")

TOKEN = os.environ.get("TOKEN", "").strip()
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))  # например: -1003761925434

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
# -------------------------------


def start_cmd(update, context):
    update.message.reply_text("Бот работает ✅\nКоманды: /signal")


def signal_cmd(update, context):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text="🚀 ТЕСТ СИГНАЛ\n\nMOEX\nBUY\nTP: 123\nSL: 120")
    update.message.reply_text("Отправил в канал ✅")


def main():
    if not TOKEN:
        raise ValueError("TOKEN не задан. Добавь в Render Environment Variables: TOKEN=...")

    if CHANNEL_ID == 0:
        raise ValueError("CHANNEL_ID не задан. Добавь в Render Environment Variables: CHANNEL_ID=-100...")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("signal", signal_cmd))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
