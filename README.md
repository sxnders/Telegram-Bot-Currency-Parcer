# 💹 BurmaldaBot — Telegram-бот курсов валют

> Единая точка доступа к курсам ЦБ РФ, криптовалютам и золоту прямо в Telegram

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-4.x-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://github.com/eternnoir/pyTelegramBotAPI)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## О проекте

**FinBot** агрегирует финансовые данные из трёх независимых источников и отдаёт их одной командой — без рекламы, без регистрации, без лишних кликов.

| Источник | Данные | Метод |
|---|---|---|
| 🏦 ЦБ РФ (`cbr.ru`) | USD, EUR, CNY | HTML-парсинг |
| 🪙 CoinGecko API | BTC, ETH | REST API |
| 🥇 GoldAPI.io | XAU / унция | REST API |

Курсы кэшируются в локальной SQLite-базе и обновляются автоматически каждые 6 часов — команда `/rates` отвечает мгновенно из БД, не нагружая внешние сервисы.

---

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие и список доступных команд |
| `/help` | Краткая справка |
| `/rates` | Актуальные курсы USD, EUR, CNY, BTC, ETH и золота |

### Пример вывода `/rates`

```
📅 Курсы ЦБ РФ на 2026-06-11

💵 USD: 71.9077 ₽
💶 EUR: 82.9743 ₽
💴 CNY: 10.6064 ₽

🪙 Криптовалюты

₿  BTC: $62,640.00
🔷 ETH: $1,642.69

🏅 Золото

XAU: $4,089.20 / унция
```

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/finbot.git
cd finbot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Задать токен бота

Получите токен у [@BotFather](https://t.me/BotFather) и экспортируйте переменную окружения:

```bash
# Linux / macOS
export TOKEN=ваш_токен_здесь

# Windows (PowerShell)
$env:TOKEN = "ваш_токен_здесь"
```

> ⚠️ Никогда не коммитьте токен в репозиторий. Используйте `.env`-файл или секреты платформы.

### 4. Запустить бота

```bash
python bot.py
```

При первом запуске автоматически:
- инициализируется база данных `rates.db`
- выполняется первое обновление всех курсов
- запускается планировщик (обновление каждые 6 ч)

---

## Развёртывание на Railway

1. Форкните репозиторий на GitHub
2. Создайте новый проект на [railway.app](https://railway.app) → **Deploy from GitHub repo**
3. В разделе **Variables** добавьте переменную `TOKEN` со значением токена бота
4. Railway автоматически обнаружит `Procfile` и запустит воркер:

```
worker: python bot.py
```

Бот будет работать круглосуточно в облаке без дополнительной настройки.

---

## Структура проекта

```
finbot/
├── bot.py           # Telegram-бот: обработчики команд, форматирование вывода
├── parcer.py        # Парсинг данных, работа с SQLite
├── requirements.txt # Зависимости Python
├── Procfile         # Конфигурация для Railway
└── rates.db         # База данных SQLite (создаётся автоматически)
```

### Архитектура

```
Telegram ──► bot.py ──► parcer.py ──► rates.db
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           cbr.ru      CoinGecko       GoldAPI.io
         (HTML)        (REST API)      (REST API)
```

### Схема базы данных

```sql
-- Курсы ЦБ РФ
rates(id, currency_code, rate, rate_date, created_at)
  UNIQUE(currency_code, rate_date)

-- Криптовалюты
crypto_rates(id, currency_code, price_usd, rate_date, created_at)
  UNIQUE(currency_code, rate_date)

-- Золото
gold_rates(id, price_usd, rate_date, created_at)
  UNIQUE(rate_date)
```

Ограничение `UNIQUE` + `INSERT OR REPLACE` обеспечивает идемпотентность: повторные запросы в течение дня обновляют запись без дублирования.

---

## Стек технологий

| Технология | Назначение |
|---|---|
| Python 3.11 | Основной язык |
| pyTelegramBotAPI | Обёртка над Telegram Bot API |
| Requests | HTTP-запросы к внешним API |
| BeautifulSoup4 | Парсинг HTML-таблицы cbr.ru |
| SQLite3 | Локальное хранение курсов (встроен в Python) |
| APScheduler | Фоновое обновление курсов по расписанию |

---

## Обработка ошибок

Бот устойчив к частичной недоступности источников: если один из трёх API недоступен, остальные разделы отображаются корректно с сообщением `😔 Не удалось получить данные` по недоступному блоку.

---

## Команда

Проект разработан в рамках дисциплины **«Проектный практикум 1A»**, УрФУ, команда **Бурмалда**:

- **Зубов Никита** — тимлид, модуль парсинга
- **Гордеев Александр** — разработка Telegram-бота
- **Бусурин Максим** — проектирование БД и архитектуры
