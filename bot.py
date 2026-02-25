import os
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

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
# ---------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает ✅")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 ТЕСТ СИГНАЛ\nMOEX\nBUY"
    )
    await update.message.reply_text("Отправил в канал ✅")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
