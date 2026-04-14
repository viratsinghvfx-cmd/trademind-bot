import requests
import os
import time
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== PRICE =====
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data["price"])

# ===== RSI =====
def get_rsi():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
    data = requests.get(url).json()

    closes = [float(x[4]) for x in data]

    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

# ===== SIGNAL LOGIC =====
def get_signal(price, rsi):
    if rsi < 30 and price < 74000:
        return "🚀 STRONG BUY", "Oversold + Support zone"
    elif rsi < 40:
        return "📈 BUY", "Recovering market"
    elif rsi > 70 and price > 76000:
        return "🔻 STRONG SELL", "Overbought + Resistance"
    elif rsi > 60:
        return "📉 SELL", "Weakness starting"
    else:
        return "⏸ WAIT", "No clear opportunity"

# ===== MESSAGE FORMAT =====
def build_message():
    price = get_price()
    rsi = get_rsi()
    signal, reason = get_signal(price, rsi)

    msg = f"""
📊 BTC Price: {price}

📈 Signal: {signal}
🧠 Reason: {reason}

📉 RSI: {rsi}
"""
    return msg

# ===== COMMANDS =====
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 Smart Trading Bot Active!\nType anything for signal.")

def price_cmd(update: Update, context: CallbackContext):
    price = get_price()
    update.message.reply_text(f"💰 BTC Price: {price}")

def signal_cmd(update: Update, context: CallbackContext):
    msg = build_message()
    update.message.reply_text(msg)

def handle_message(update: Update, context: CallbackContext):
    try:
        msg = build_message()
        update.message.reply_text(msg)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# ===== AUTO ALERT SYSTEM =====
def auto_trader(bot):
    last_signal = ""

    while True:
        try:
            price = get_price()
            rsi = get_rsi()
            signal, reason = get_signal(price, rsi)

            current = f"{signal}-{round(price,0)}"

            # only send when strong opportunity
            if "STRONG" in signal and current != last_signal:
                message = f"""
🔥 TRADE ALERT 🔥

📊 Price: {price}
📈 Signal: {signal}
📉 RSI: {rsi}
🧠 {reason}
"""
                bot.send_message(chat_id=CHAT_ID, text=message)
                last_signal = current

            # price alert
            if price > 77000:
                bot.send_message(chat_id=CHAT_ID, text=f"🚀 Breakout! BTC > 77000 ({price})")

            if price < 73000:
                bot.send_message(chat_id=CHAT_ID, text=f"🔻 Breakdown! BTC < 73000 ({price})")

        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Auto error: {e}")

        time.sleep(60)

# ===== MAIN =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price_cmd))
    dp.add_handler(CommandHandler("signal", signal_cmd))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()

    # start auto thread
    threading.Thread(target=auto_trader, args=(updater.bot,), daemon=True).start()

    updater.idle()

if __name__ == "__main__":
    main()
