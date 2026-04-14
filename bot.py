import requests
import time
import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

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

# Command: /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 TradeMind Bot Active!\nType anything to get signal.")

# Message handler
def handle_message(update: Update, context: CallbackContext):
    price = get_price()
    signal, reason = get_signal(price)

    message = f"BTC Price: {price}\nSignal: {signal}\nReason: {reason}"
    update.message.reply_text(message)

# Background signal sender
def send_signal():
    price = get_price()
    signal, reason = get_signal(price)

    message = f"📊 Auto Signal\nBTC: {price}\nSignal: {signal}\nReason: {reason}"
    bot.send_message(chat_id=CHAT_ID, text=message)

# Main
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()

# Background loop
while True:
    try:
        send_signal()
        time.sleep(60)
    except Exception as e:
        print(e)
        time.sleep(10)
