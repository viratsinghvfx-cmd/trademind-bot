import requests
import time
import os
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data['price'])

def get_signal(price):
    if price > 75000:
        return "BUY", "Breakout above resistance"
    elif price < 74000:
        return "SELL", "Breakdown below support"
    else:
        return "WAIT", "Market sideways"

while True:
    try:
        price = get_price()
        signal, reason = get_signal(price)

        message = f"BTC Price: {price}\nSignal: {signal}\nReason: {reason}"

        bot.send_message(chat_id=CHAT_ID, text=message)

        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(10)
