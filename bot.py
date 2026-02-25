import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# твои модули
from scanner import scan_once
from charts import make_chart

# ====== НАСТРОЙКИ через ENV ======
TOKEN = os.environ.get("TOKEN", "").strip()
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))  # например: -1003761925434

INTERVAL_MIN = int(os.environ.get("TF_MIN", "15"))
SCAN_EVERY_SEC = int(os.environ.get("SCAN_EVERY_SEC", "300"))
ANOMALY_K = float(os.environ.get("ANOMALY_K", "3.0"))
# ================================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ru-pulsebot")

WATCH_FUTURES = ["Si", "RI", "MXI"]
WATCH_STOCKS = ["SBER", "GAZP", "LKOH", "ROSN", "GMKN", "NVTK", "TATN", "YDEX", "MGNT", "MTSS"]


# ---- HTTP сервер для Render (чтобы порт был открыт) ----
def start_http_server():
    port = int(os.environ.get("PORT", "10000"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, format, *args):
            return

    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


threading.Thread(target=start_http_server, daemon=True).start()
# -------------------------------------------------------


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает ✅\nКоманды: /signal (тест), /scan (ручной запуск)")


async def test_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 ТЕСТ СИГНАЛ\n\nMOEX FUTURES\nBUY\nTP: 123.45\nSL: 120.00"
    )
    await update.message.reply_text("Тест отправлен в канал ✅")


def send_signal_to_channel_sync(app, text: str, df, title: str):
    """
    Синхронная функция (для потока сканера).
    Отправляет текст + картинку.
    """
    # 1) текст
    app.bot.send_message(chat_id=CHANNEL_ID, text=text)

    # 2) картинка
    path = "tmp/chart.png"
    make_chart(df, title=title, path=path)
    with open(path, "rb") as f:
        app.bot.send_photo(chat_id=CHANNEL_ID, photo=f)


def scan_job_sync(app):
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
                send_signal_to_channel_sync(app, s.text, s.chart_df, title=title)
            except Exception as e:
                log.exception("send error: %s", e)
    except Exception as e:
        log.exception("scan_job error: %s", e)


def scan_loop_sync(app):
    while True:
        scan_job_sync(app)
        threading.Event().wait(SCAN_EVERY_SEC)


async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ручной запуск скана (без ожидания в фоне)
    app = context.application
    # Выполним в отдельном потоке, чтобы не блокировать обработчик
    threading.Thread(target=scan_job_sync, args=(app,), daemon=True).start()
    await update.message.reply_text("Скан запущен вручную ✅ (если были сигналы — улетели в канал)")


def main():
    if not TOKEN:
        raise ValueError("Не задан TOKEN. Добавь его в Render Environment Variables.")
    if not CHANNEL_ID:
        raise ValueError("Не задан CHANNEL_ID. Добавь его в Render Environment Variables.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("signal", test_signal))
    app.add_handler(CommandHandler("scan", scan_cmd))

    # Фоновый сканер
    threading.Thread(target=scan_loop_sync, args=(app,), daemon=True).start()

    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
