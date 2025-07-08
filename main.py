import os
import csv
import datetime
import requests
import yfinance as yf
from dotenv import load_dotenv


# Charger les variables d'environnement
load_dotenv()
TELEGRAM_TOKEN = "7905223139:AAEWxb2NMTAAdc530vBgASfZF7fIXm1cvHA"
TELEGRAM_CHAT_ID = 8018836005


def send_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("❌ Erreur d'envoi Telegram :", response.text)
    else:
        print("✅ Notification envoyée")


def initialize_trade_file_if_needed(price):
    filename = "trades.csv"
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        print("🆕 Initialisation de trades.csv")
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "price"])
            writer.writerow([datetime.datetime.now().isoformat(), price])
        message = f"🆕 Fichier trades.csv initialisé avec le prix actuel de l'ETF MSCI World : {price:.2f} €"
        send_message(price)
        return True
    return False

def get_last_trade_price():
    with open("trades.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        rows = list(reader)
        if not rows:
            return None
        return float(rows[-1][1])

def log_trade(price):
    with open("trades.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now().isoformat(), price])

def should_buy(current_price, last_price, threshold=0.0002):
    variation = (last_price - current_price) / last_price
    print(f"🔍 Variation : {-variation*100:.2f}%")
    return variation >= threshold

def main():
    ticker = yf.Ticker("EUNL.DE")
    price = ticker.history(period="1d")["Close"].iloc[-1]
    last_price = get_last_trade_price()
    variation = (last_price - price) / last_price
    print(f"📊 Prix actuel : {price:.2f} €")

    # Initialisation
    if initialize_trade_file_if_needed(price):
        return

    last_price = get_last_trade_price()
    if last_price is None:
        print("⚠️ Impossible de lire le dernier prix.")
        return

    # Stratégie d'achat simple
    if should_buy(price, last_price):
        log_trade(price)
        message = f"✅ Achat simulé de l'ETF MSCI World à {price:.2f} €\n 📊 Prix actuel : {price:.2f} €,\n 🔍 Variation depuis le dernier call: {-variation*100:.2f}% "
        send_message(message)
    else:
        print("⏳ Pas d'achat simulé aujourd'hui.")
        message = f"⏳ Pas d'achat simulé aujourd'hui.\n 📊 Prix actuel : {price:.2f} €,\n 🔍 Variation depuis le dernier call: {-variation*100:.2f}% "
        send_message(message)

if __name__ == "__main__":
    main()
    
