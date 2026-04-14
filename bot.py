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
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, timeout=5)
        data = res.json()
        return float(data["price"]) if "price" in data else None
    except:
        return None

# ===== RSI =====
def get_rsi():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
        data = requests.get(url).json()

        closes = [float(x[4]) for x in data]

        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(abs(min(diff, 0)))

        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
    except:
        return None

# ===== EMA =====
def get_ema():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
        data = requests.get(url).json()
        closes = [float(x[4]) for x in data]

        ema = sum(closes[-9:]) / 9
        return round(ema, 2)
    except:
        return None

# ===== SIGNAL =====
def get_signal(price, rsi, ema):
    if price is None or rsi is None or ema is None:
        return "⚠️ ERROR", "Data fetch issue"

    if price > ema and rsi < 35:
        return "🚀 STRONG BUY", "Price above EMA + RSI oversold recovery"
    elif price < ema and rsi > 65:
        return "🔻 STRONG SELL", "Price below EMA + RSI overbought"
    elif rsi < 40:
        return "📈 BUY", "Market gaining strength"
    elif rsi > 60:
        return "📉 SELL", "Market weakening"
    else:
        return "⏸ WAIT", "No clear trend"

# ===== JARVIS RESPONSE =====
def jarvis_reply(text):
    text = text.lower()

    if "buy" in text:
        return "🧠 Jarvis: Buying is good only when RSI low & trend up. Avoid FOMO."

    if "sell" in text:
        return "🧠 Jarvis: Sell when market is overbought or losing strength."

    if "safe" in text:
        return "🧠 Jarvis: No trade is safest trade. Wait for confirmation."

    return "🧠 Jarvis: Market patience = profit. Don't rush trades."

# ===== MESSAGE =====
def build_message():
    price = get_price()
    rsi = get_rsi()
    ema = get_ema()

    if price is None or rsi is None or ema is None:
        return "⚠️ Data fetch failed"

    signal, reason = get_signal(price, rsi, ema)

    return f"""
🤖 TradeMind JARVIS Report

📊 Price: {price}
📉 RSI: {rsi}
📈 EMA: {ema}

📢 Signal: {signal}
🧠 Reason: {reason}
"""

# ===== COMMANDS =====
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Jarvis Activated!\nAsk me anything about market.")

def signal_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(build_message())

def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text

    # normal signal
    report = build_message()

    # jarvis advice
    advice = jarvis_reply(user_text)

    update.message.reply_text(report + "\n\n" + advice)

# ===== AUTO SYSTEM =====
def auto_trader(bot):
    last_alert = ""

    while True:
        try:
            price = get_price()
            rsi = get_rsi()
            ema = get_ema()

            if not price or not rsi or not ema:
                time.sleep(60)
                continue

            signal, reason = get_signal(price, rsi, ema)

            key = f"{signal}-{round(price)}"

            if "STRONG" in signal and key != last_alert:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"""
🔥 JARVIS ALERT 🔥

📊 Price: {price}
📉 RSI: {rsi}
📈 EMA: {ema}

📢 {signal}
🧠 {reason}
"""
                )
                last_alert = key

        except:
            pass

        time.sleep(60)

# ===== MAIN =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("signal", signal_cmd))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()

    threading.Thread(target=auto_trader, args=(updater.bot,), daemon=True).start()

    updater.idle()

if __name__ == "__main__":
    main()
