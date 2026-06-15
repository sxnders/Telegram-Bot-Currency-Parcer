import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import os

from parcer import (
    init_db,
    get_cbr_rates, save_rates_to_db, get_latest_rates_from_db,
    get_crypto_rates, save_crypto_to_db, get_latest_crypto_from_db,
    get_gold_price, save_gold_to_db, get_latest_gold_from_db,
)

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


def update_all_rates():
    """Фоновое обновление всех курсов"""
    print("Обновляю курсы...")

    rates = get_cbr_rates()
    if rates:
        save_rates_to_db(rates)

    crypto = get_crypto_rates()
    if crypto:
        save_crypto_to_db(crypto)

    gold = get_gold_price()
    if gold:
        save_gold_to_db(gold)

    print("Курсы обновлены.")


def format_rates_message(cbr_data, crypto_data, gold_data):
    lines = []

    if cbr_data and cbr_data.get("rates"):
        rates = cbr_data["rates"]
        date = cbr_data["date"]
        lines.append(f"📅 Курсы ЦБ РФ на {date}\n")
        lines.append(f"💵 USD: {rates.get('USD', 'нет данных')} ₽")
        lines.append(f"💶 EUR: {rates.get('EUR', 'нет данных')} ₽")
        lines.append(f"💴 CNY: {rates.get('CNY', 'нет данных')} ₽")
    else:
        lines.append("😔 Не удалось получить курсы ЦБ РФ.")

    lines.append("")

    if crypto_data and crypto_data.get("rates"):
        rates = crypto_data["rates"]
        lines.append("🪙 Криптовалюты\n")
        lines.append(f"₿  BTC: ${rates.get('BTC', 'нет данных'):,.2f}")
        lines.append(f"🔷 ETH: ${rates.get('ETH', 'нет данных'):,.2f}")
    else:
        lines.append("😔 Не удалось получить курсы криптовалют.")

    lines.append("")

    if gold_data:
        lines.append("🏅 Золото\n")
        lines.append(f"XAU: ${gold_data.get('price', 'нет данных'):,.2f} / унция")
    else:
        lines.append("😔 Не удалось получить цену золота.")

    return "\n".join(lines)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "🤖 Привет! Я бот курсов валют.\n\n"
        "Доступные команды:\n"
        "/start — запуск\n"
        "/help — помощь\n"
        "/rates — курсы USD, EUR, CNY, BTC, ETH и золото"
    )


@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(
        message.chat.id,
        "💡 Команды бота:\n"
        "/rates — показать курсы валют ЦБ РФ, крипту и золото"
    )


@bot.message_handler(commands=["rates"])
def send_rates(message):
    cbr_data = get_latest_rates_from_db()
    crypto_data = get_latest_crypto_from_db()
    gold_data = get_latest_gold_from_db()

    bot.send_message(message.chat.id, format_rates_message(cbr_data, crypto_data, gold_data))


@bot.message_handler(content_types=["text"])
def unknown_message(message):
    bot.send_message(
        message.chat.id,
        "❌ Я тебя не понимаю.\nИспользуй /start, /help или /rates"
    )


if __name__ == "__main__":
    init_db()

    update_all_rates()

    scheduler = BackgroundScheduler()
    scheduler.add_job(update_all_rates, 'interval', hours=6)
    scheduler.start()

    print("Бот запущен...")
    bot.infinity_polling()
