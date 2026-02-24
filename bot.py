import logging
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8655371651:AAGrecLlCakLa7Pcv5JTG94BPpiRFw4qbQc"

logging.basicConfig(level=logging.INFO)

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

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Бот работает ✅")

def main():
    threading.Thread(target=start_http_server, daemon=True).start()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
