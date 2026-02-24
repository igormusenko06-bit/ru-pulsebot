import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("RU-PulseBot запущен 🚀")

async def signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сигналы скоро будут подключены 📊")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signals", signals))

app.run_polling()
