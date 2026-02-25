import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Bot
from telegram.ext import Updater, CommandHandler

from scanner import scan_once
from charts import make_chart

# ====== НАСТРОЙКИ ======
TOKEN = "8655371651:AAGrecLlCakLa7Pcv5JTG94BPpiRFw4qbQc"
CHANNEL_ID = -1003761925434

INTERVAL_MIN = 15
SCAN_EVERY_SEC = 300
ANOMALY_K = 3.0
# =======================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ru-pulsebot")

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


WATCH_FUTURES = [
    "Si",
    "RI",
    "MXI",
]

WATCH_STOCKS = [
    "SBER", "GAZP", "LKOH", "ROSN", "GMKN",
    "NVTK", "TATN", "YDEX", "MGNT", "MTSS"
]


def start_cmd(update, context):
    update.message.reply_text(
        "Бот работает ✅\n"
        "Команды:\n"
        "/signal — тест\n"
        "/scan — ручной запуск сканера"
    )


def send_signal_to_channel(bot: Bot, text: str, df, title: str):
    bot.send_message(chat_id=CHANNEL_ID, text=text)

    path = "tmp/chart.png"
    make_chart(df, title=title, path=path)

    with open(path, "rb") as f:
        bot.send_photo(chat_id=CHANNEL_ID, photo=f)


def scan_job(bot: Bot):
    try:
        signals = scan_once(
            watch_futures=WATCH_FUTURES,
            watch_stocks=WATCH_STOCKS,
            interval_min=INTERVAL_MIN,
            anomaly_k=ANOMALY_K,
        )

        for s in signals:
            try:
                title = f"{s.symbol} • {s.tf}"
                send_signal_to_channel(bot, s.text, s.chart_df, title)
            except Exception as e:
                log.exception("Ошибка отправки: %s", e)

    except Exception as e:
        log.exception("Ошибка сканера: %s", e)


def scan_loop(bot: Bot):
    while True:
        scan_job(bot)
        threading.Event().wait(SCAN_EVERY_SEC)


def scan_cmd(update, context):
    bot = Bot(token=TOKEN)
    scan_job(bot)
    update.message.reply_text("Скан выполнен вручную ✅")


def test_signal(update, context):
    bot = Bot(token=TOKEN)
    bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 ТЕСТ СИГНАЛ\n\nMOEX FUTURES\nBUY\nTP: 123.45\nSL: 120.00"
    )
    update.message.reply_text("Тест отправлен в канал ✅")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("signal", test_signal))
    dp.add_handler(CommandHandler("scan", scan_cmd))

    bot = Bot(token=TOKEN)
    threading.Thread(target=scan_loop, args=(bot,), daemon=True).start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
