import requests
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TOKEN")

# BTC price
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data["price"])

# Signal logic
def get_signal(price):
    if price > 75000:
        return "BUY", "Breakout above resistance"
    elif price < 74000:
        return "SELL", "Breakdown below support"
    else:
        return "WAIT", "Market sideways"

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 TradeMind Bot Active!\nType anything to get signal.")

# reply to any message
def handle_message(update: Update, context: CallbackContext):
    price = get_price()
    signal, reason = get_signal(price)

    message = f"BTC Price: {price}\nSignal: {signal}\nReason: {reason}"
    update.message.reply_text(message)

# setup
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# start bot
updater.start_polling()
updater.idle()
