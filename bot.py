import requests
import time
from telegram import Bot

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

bot = Bot(token=TOKEN)

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data['price'])

def get_signal(price):
    if price > 75000:
        return "BUY", "Breakout above resistance"
    elif price < 74400:
        return "SELL", "Breakdown below support"
    else:
        return "WAIT", "Market sideways"

def send_signal():
    price = get_price()
    action, reason = get_signal(price)

    message = f"""
🚨 BTC SIGNAL

Price: {price}

ACTION: {action}

WHY:
- {reason}

PLAN:
SL: Manage risk
Target: Momentum based
"""

    bot.send_message(chat_id=CHAT_ID, text=message)

while True:
    send_signal()
    time.sleep(60)
