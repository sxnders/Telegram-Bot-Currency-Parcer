Курсы валют бот 🤖
Telegram-бот для отслеживания курсов валют ЦБ РФ, криптовалют и золота.
Возможности

💵 Курсы USD, EUR, CNY от ЦБ РФ
🪙 Курсы криптовалют (BTC, ETH) через CoinGecko
🏅 Цена золота (XAU/USD)
🔄 Автообновление данных каждые 6 часов
💾 Хранение истории в SQLite

Команды
КомандаОписание/startЗапуск бота/helpСписок команд/ratesПоказать текущие курсы
Установка
bashgit clone https://github.com/yourusername/currency-bot.git
cd currency-bot
pip install -r requirements.txt
Зависимости
pyTelegramBotAPI
apscheduler
requests
beautifulsoup4
Настройка

Получите токен бота у @BotFather
Установите переменную окружения:

bashexport TOKEN="ваш_токен_бота"
Запуск
bashpython bot.py
При запуске бот сразу обновит курсы и создаст базу данных rates.db, после чего будет обновлять данные раз в 6 часов в фоновом режиме.
