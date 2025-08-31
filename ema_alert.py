import ccxt
import pandas as pd
import time
import datetime
from ta.trend import EMAIndicator
import smtplib
from email.mime.text import MIMEText

# ==========================
# Email Configuration
# ==========================
EMAIL_ADDRESS = "guptadharminder@gmail.com"
EMAIL_PASSWORD = "pvxj uzej eybu uqqb"   # Gmail App Password (16 char)
TO_EMAIL = "guptadharminder@gmail.com"

def send_email_alert(subject, body):
    try:
        print("📧 Sending email...")  # debug
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent!")
    except Exception as e:
        print("❌ Email send error:", e)

# ==========================
# Exchange Setup
# ==========================
exchange = ccxt.binance()
symbol = "ETH/USDT"
timeframe = "1m"
prev_cross = None

# ==========================
# Signal Check Function
# ==========================
def check_signal():
    global prev_cross
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
    df = pd.DataFrame(bars, columns=['time','open','high','low','close','volume'])
    ema9 = EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema9'] = ema9

    # Detect EMA cross
    if df['close'].iloc[-1] > df['ema9'].iloc[-1] and df['close'].iloc[-2] <= df['ema9'].iloc[-2]:
        cross = "up"
    elif df['close'].iloc[-1] < df['ema9'].iloc[-1] and df['close'].iloc[-2] >= df['ema9'].iloc[-2]:
        cross = "down"
    else:
        cross = None

    if cross and cross != prev_cross:
        msg = f"[{datetime.datetime.now()}] EMA 9 CROSS {cross.upper()} on {symbol}"
        print(msg)
        send_email_alert("EMA 9 Crossover Alert", msg)
        prev_cross = cross

# ==========================
# Main Loop
# ==========================
while True:
    try:
        check_signal()
        time.sleep(60)  # 1-minute wait if no error
    except Exception as e:
        print("Error:", e)
        time.sleep(10)  # retry after 10 sec
