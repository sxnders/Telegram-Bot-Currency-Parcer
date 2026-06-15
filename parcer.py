import sqlite3
from datetime import datetime
 
import requests
from bs4 import BeautifulSoup
 
DB_NAME = "rates.db"
CBR_URL = "https://www.cbr.ru/currency_base/daily/"
 
 
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT NOT NULL,
            rate REAL NOT NULL,
            rate_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(currency_code, rate_date)
        )
    """)
 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT NOT NULL,
            price_usd REAL NOT NULL,
            rate_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(currency_code, rate_date)
        )
    """)
 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_usd REAL NOT NULL,
            rate_date TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
 
    conn.commit()
    conn.close()
 
 
def get_cbr_rates():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
 
    try:
        response = requests.get(CBR_URL, headers=headers, timeout=10)
        response.raise_for_status()
 
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="data")
 
        if not table:
            print("Таблица не найдена на cbr.ru")
            return None
 
        rates = {}
        rows = table.find_all("tr")[1:]
 
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                code = cols[1].text.strip()
                if code in ["USD", "EUR", "CNY"]:
                    rate = float(cols[4].text.strip().replace(",", "."))
                    rates[code] = rate
 
        return rates if rates else None
 
    except Exception as e:
        print(f"Ошибка при получении курсов ЦБ РФ: {e}")
        return None
 
 
def save_rates_to_db(rates):
    if not rates:
        print("Нет данных ЦБ РФ для сохранения")
        return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
 
    for code, rate in rates.items():
        cursor.execute("""
            INSERT OR REPLACE INTO rates (currency_code, rate, rate_date)
            VALUES (?, ?, ?)
        """, (code, rate, today))
 
    conn.commit()
    conn.close()
    print("Данные ЦБ РФ сохранены в базу данных")
 
 
def get_latest_rates_from_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT currency_code, rate, rate_date
        FROM rates
        WHERE rate_date = (SELECT MAX(rate_date) FROM rates)
        ORDER BY currency_code
    """)
 
    rows = cursor.fetchall()
    conn.close()
 
    if not rows:
        return None
 
    return {
        "date": rows[0][2],
        "rates": {row[0]: row[1] for row in rows}
    }
 
 
def get_crypto_rates():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-cg-demo-api-key": "CG-5j1akPJXBXpxY5voveA6Qxim"
    }
 
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
 
        rates = {}
        if "bitcoin" in data:
            rates["BTC"] = data["bitcoin"]["usd"]
        if "ethereum" in data:
            rates["ETH"] = data["ethereum"]["usd"]
 
        return rates if rates else None
 
    except Exception as e:
        print(f"Ошибка CoinGecko: {e}")
        return None
 
 
def save_crypto_to_db(rates):
    if not rates:
        print("Нет данных криптовалют для сохранения")
        return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
 
    for code, price in rates.items():
        cursor.execute("""
            INSERT OR REPLACE INTO crypto_rates (currency_code, price_usd, rate_date)
            VALUES (?, ?, ?)
        """, (code, price, today))
 
    conn.commit()
    conn.close()
    print("Данные криптовалют сохранены в базу данных")
 
 
def get_latest_crypto_from_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT currency_code, price_usd, rate_date
        FROM crypto_rates
        WHERE rate_date = (SELECT MAX(rate_date) FROM crypto_rates)
        ORDER BY currency_code
    """)
 
    rows = cursor.fetchall()
    conn.close()
 
    if not rows:
        return None
 
    return {
        "date": rows[0][2],
        "rates": {row[0]: row[1] for row in rows}
    }
 
def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": "goldapi-6cfe5fa21dea99ae354a0b37d4411531-io",
        "User-Agent": "Mozilla/5.0"
    }
 
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return round(data["price"], 2)
 
    except Exception as e:
        print(f"Ошибка GoldAPI: {e}")
        return None
 
 
def save_gold_to_db(price):
    if price is None:
        print("Нет данных по золоту для сохранения")
        return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
 
    cursor.execute("""
        INSERT OR REPLACE INTO gold_rates (price_usd, rate_date)
        VALUES (?, ?)
    """, (price, today))
 
    conn.commit()
    conn.close()
    print("Данные по золоту сохранены в базу данных")
 
 
def get_latest_gold_from_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT price_usd, rate_date
        FROM gold_rates
        WHERE rate_date = (SELECT MAX(rate_date) FROM gold_rates)
    """)
 
    row = cursor.fetchone()
    conn.close()
 
    if not row:
        return None
 
    return {"price": row[0], "date": row[1]}
 
 
if __name__ == "__main__":
    init_db()
 
    rates = get_cbr_rates()
    save_rates_to_db(rates)
    print(get_latest_rates_from_db())
 
    crypto = get_crypto_rates()
    save_crypto_to_db(crypto)
    print(get_latest_crypto_from_db())
 
    gold = get_gold_price()
    save_gold_to_db(gold)
    print(get_latest_gold_from_db())