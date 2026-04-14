import requests
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TOKEN")

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data["price"])

def get_signal(price):
    if price > 75000:
        return "BUY", "Breakout above resistance"
    elif price < 74000:
        return "SELL", "Breakdown below support"
    else:
        return "WAIT", "Market sideways"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 TradeMind Bot Active!\nType anything to get signal.")

def handle_message(update: Update, context: CallbackContext):
    try:
        price = get_price()
        signal, reason = get_signal(price)

        message = f"""📊 BTC Price: {price}
📈 Signal: {signal}
🧠 Reason: {reason}"""

        update.message.reply_text(message)

    except Exception as e:
        update.message.reply_text("Error occurred")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text, handle_message))

updater.start_polling()
updater.idle()
