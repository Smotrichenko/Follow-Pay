<div align="center">

# 🎓 *Follow&Pay*

**Платформа для монетизации контента и управления подписками**

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)]()
[![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)]()
[![DRF](https://img.shields.io/badge/DRF-3.16-red?logo=django)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)]()
[![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)]()
[![Celery](https://img.shields.io/badge/Celery-✓-green?logo=celery)]()
[![Stripe](https://img.shields.io/badge/Stripe-✓-purple?logo=stripe)]()
[![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen)]()

</div>

## 📋 Оглавление
- [Идея проекта](#-идея-проекта)
- [Возможности](#-основные-возможности)
- [Архитектура](#-архитектура-проекта)
- [Технические особенности](#-технические-особенности)
- [API](#-api-endpoints)
- [Тестирование](#-тестирование)
- [Бизнес-логика](#-бизнес-логика)
- [Перспективы развития](#-перспективы-развития)
- [Запуск проекта](#-установка-и-запуск-проекта)


**Follow&Pay** — это веб-платформа для монетизации контента, позволяющая авторам публиковать платные материалы и получать доход от подписчиков.

Проект решает задачу создания простой и удобной системы взаимодействия между авторами и их аудиторией, где:
- авторы получают инструмент для монетизации контента
- пользователи — доступ к эксклюзивным материалам
- система автоматически управляет оплатами, доступами и уведомлениями

##  💡  *Идея проекта*
В современном интернете всё больше авторов создают уникальный контент: статьи, обучающие материалы, инсайты, аналитика.

Однако:
- не у всех есть удобный инструмент для монетизации
- пользователям сложно находить и поддерживать авторов
- интеграция платежей и уведомлений требует сложной настройки

**Follow&Pay** решает эти проблемы, предоставляя единый сервис, где:
- автор может за 2–3 действия начать зарабатывать
- пользователь может быстро оформить подписку
- система автоматически контролирует доступ к контенту

## 🎯 *Основные возможности*
### 👤 Пользователи
- Регистрация и вход по номеру телефона (без пароля, через одноразовый код)
- Безопасная авторизация через JWT
- Привязка Telegram для получения уведомлений

### 👨‍🎨 Авторы
- Создание профиля автора
- Установка стоимости подписки
- Автоматическая интеграция с платежной системой Stripe
- Управление своим контентом

### 📝 Контент
- Создание постов (платных и бесплатных)
- Ограничение доступа к платным постам
- Публикация контента с уведомлением подписчиков

### 💳 Платежная система
- Оплата через Stripe Checkout
- Обработка webhook'ов
- Автоматическая активация подписки после оплаты
- Связка платежей и пользователей

### 🔔 Уведомления
- Уведомления через Telegram:
  - о покупке подписки
  - о новых постах
- Асинхронная обработка через Celery

## 🏗 Архитектура проекта

Проект построен по модульному принципу (Django apps):

- `users` — управление пользователями, авторизация, Telegram
- `creators` — логика авторов и их подписок
- `posts` — публикация и доступ к контенту
- `subscriptions` — управление подписками
- `payments` — интеграция со Stripe
- `web` — frontend (templates + Bootstrap)

Такое разделение обеспечивает:
- масштабируемость
- читаемость кода
- удобство тестирования

## ⚙️ Технические особенности

- REST API на Django Rest Framework
- Авторизация без пароля (OTP через телефон)
- JWT-аутентификация
- Асинхронные задачи (Celery + Redis)
- Интеграция с внешними API:
  - Stripe (платежи)
  - Telegram (уведомления)
- Контейнеризация:
  - Docker
  - Docker Compose
  - Nginx (reverse proxy)
- PostgreSQL как основная БД

## 🧪 Тестирование

- Используется pytest
- Покрытие проекта более 80%
- Тестируются:
  - API endpoints
  - бизнес-логика
  - платежи и подписки
  - Telegram интеграция

## 📈 Бизнес-логика

Проект реализует полный цикл:

1. Пользователь регистрируется по номеру телефона
2. При желании становится автором
3. Публикует контент
4. Устанавливает цену подписки
5. Другой пользователь оформляет подписку через Stripe
6. После оплаты:
   - создаётся подписка
   - открывается доступ к контенту
   - отправляется уведомление в Telegram
7. При публикации нового поста:
   - подписчики получают уведомление

## 🚀 Перспективы развития

- Добавление лайков и комментариев
- Лента рекомендаций
- Аналитика для авторов
- Поддержка нескольких тарифов

## ⚙️ Установка и запуск проекта

### Клонировать репозиторий
```
git clone https://github.com/Smotrichenko/follow-pay.git
cd follow-pay
```

### 1️⃣ Создать файл .env
В корне проекта создать файл .env на основе шаблона:
```
SECRET_KEY=your_secret_key
DEBUG=True

NAME=coursebox
USER=postgres
PASSWORD=postgres
HOST=db
PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### 2️⃣ Запуск всех сервисов
```
docker compose up -d --build
docker compose exec backend python manage.py migrate
```
После запуска будут подняты:
- backend (Django)
- nginx
- db (PostgreSQL)
- redis
- celery (worker)
- celery_beat (scheduler)

## 🔗 *Stripe (локальная разработка)*

Используется Stripe CLI:
```commandline
stripe listen --forward-to localhost:8000/api/payments/stripe/webhook/
```
Секрет вставить в **.env:**
```commandline
STRIPE_WEBHOOK_SERCET=whsec_...
```
## 🤖 *Telegram*
1. Создать бота через BotFather
2. Указать токен в **.env**
3. Установить webhook:
```commandline
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<ngrok>/api/users/telegram/webhook/
```

## *🧪 Тесты*
Запуск тестов локально:
```
poetry run python manage.py test
```
Покрытие:
```
coverage run manage.py test
coverage report
```

## *🔍 Проверка работы сервисов*
### Backend
```
http://127.0.0.1:8000/swagger/
```
### PostgreSQL
```
docker exec -it followpay_db psql -U ${DB_USER} -d ${DB_NAME} -c "\dt"
```
### Redis
```
docker exec -it followpay_redis redis-cli ping
```
Ответ должен быть:
```
PONG
```
### Celery Worker
```
docker compose logs -f celery
```
### Celery Beat
```
docker compose logs -f celery_beat
```

## *🔐 API (endpoints)*
### Пользователи
- `POST /api/auth/request-code/` — запрос кода подтверждения
- `POST /api/auth/verify-code/` — вход по коду
- `GET /api/users/me/` — профиль текущего пользователя

### Авторы
- `GET /api/creators/` — список авторов
- `POST /api/creators/` — стать автором
- `GET /api/creators/{id}/` — профиль автора

### Посты
- `GET /api/posts/` — лента постов
- `GET /api/posts/{id}/` — детали поста (проверяет доступ)
- `POST /api/posts/` — создать пост (только автор)

### Подписки
- `GET /api/subscriptions/` — мои подписки
- `POST /api/subscriptions/create-checkout/` — оплата подписки

Полная документация доступна по `/api/docs/`

## *📦 Локальный запуск без Docker*
```
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## *🛑 Остановка контейнеров*
```
docker compose down
```



