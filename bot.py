import requests
import os
import time
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===== FORCE CLEAN TOKEN =====
TOKEN = os.getenv("TOKEN").strip()
CHAT_ID = os.getenv("CHAT_ID")


# ===== PRICE =====
def get_price():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        return float(res["price"])
    except:
        try:
            res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5).json()
            return float(res["bitcoin"]["usd"])
        except:
            return None


# ===== RSI =====
def get_rsi():
    try:
        data = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50").json()
        closes = [float(x[4]) for x in data]

        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(abs(min(diff, 0)))

        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14

        if avg_loss == 0:
            return 50

        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
    except:
        return 50


# ===== EMA =====
def get_ema():
    try:
        data = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=20").json()
        closes = [float(x[4]) for x in data]
        return round(sum(closes[-9:]) / 9, 2)
    except:
        return None


# ===== SIGNAL =====
def get_signal(price, rsi, ema):
    if price is None:
        return "⚠️ ERROR", "Market data unavailable"

    if ema is None:
        return "⏸ WAIT", "Trend unclear"

    if price > ema and rsi < 35:
        return "🚀 STRONG BUY", "Oversold + Uptrend"
    elif price < ema and rsi > 65:
        return "🔻 STRONG SELL", "Overbought + Downtrend"
    elif rsi < 40:
        return "📈 BUY", "Recovery phase"
    elif rsi > 60:
        return "📉 SELL", "Weakness"
    else:
        return "⏸ WAIT", "Sideways market"


# ===== MESSAGE =====
def build_message():
    price = get_price()
    rsi = get_rsi()
    ema = get_ema()

    if price is None:
        return "⚠️ Data fetch failed"

    signal, reason = get_signal(price, rsi, ema)

    return f"""🤖 JARVIS REPORT

📊 Price: {price}
📉 RSI: {rsi}
📈 EMA: {ema}

📢 Signal: {signal}
🧠 Reason: {reason}
"""


# ===== JARVIS AI =====
def jarvis_reply(text):
    text = text.lower()

    if "buy" in text:
        return "🧠 Jarvis: Buy only when RSI low & trend strong."

    if "sell" in text:
        return "🧠 Jarvis: Sell when market weak or overbought."

    if "safe" in text:
        return "🧠 Jarvis: No trade = safest trade."

    return "🧠 Jarvis: Discipline > Emotion."


# ===== HANDLERS =====
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Jarvis Activated!")


def handle(update: Update, context: CallbackContext):
    report = build_message()
    advice = jarvis_reply(update.message.text)

    update.message.reply_text(report + "\n\n" + advice)


# ===== AUTO ALERT =====
def auto_trader(bot):
    last_alert = ""

    while True:
        try:
            price = get_price()
            rsi = get_rsi()
            ema = get_ema()

            if price is None:
                time.sleep(60)
                continue

            signal, reason = get_signal(price, rsi, ema)

            key = f"{signal}-{round(price)}"

            if "STRONG" in signal and key != last_alert:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"""🔥 JARVIS ALERT 🔥

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
    dp.add_handler(MessageHandler(Filters.text, handle))

    updater.start_polling()

    threading.Thread(target=auto_trader, args=(updater.bot,), daemon=True).start()

    updater.idle()


if __name__ == "__main__":
    main()
