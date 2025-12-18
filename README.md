# YeahTube - Backend платформа для відеохостингу

## Опис проєкту

YeahTube - це повнофункціональна backend-платформа для відеохостингу, аналог YouTube. Система дозволяє користувачам завантажувати відео, створювати канали, підписуватися на інших авторів, залишати коментарі, переглядати відео та управляти плейлистами. Адміністратори мають можливість модерувати контент, видавати штрафи каналам, блокувати користувачів та аналізувати статистику платформи.

**Предметна область:** Відеохостинг з можливостями монетизації та модерації контенту

---

## Технологічний стек

- **Мова програмування:** Python 3.11
- **Веб-фреймворк:** FastAPI 0.115.6
- **ORM:** SQLAlchemy 2.0
- **Міграції:** Alembic
- **База даних:** PostgreSQL 17
- **Аутентифікація:** JWT (python-jose)
- **Валідація:** Pydantic 2.0
- **Тестування:** pytest 9.0.2
- **Контейнеризація:** Docker + Docker Compose
- **Менеджер залежностей:** uv

---

## Схема бази даних

Система включає **11 основних таблиць**, пов'язаних між собою:

### Основні сутності:
- **users** - користувачі системи
- **channels** - канали авторів
- **videos** - відеоматеріали
- **comments** - коментарі до відео
- **views** - історія переглядів
- **subscription** - підписки користувачів на канали
- **paid_subscriptions** - платні підписки
- **playlists** - плейлисти користувачів
- **playlist_video** - зв'язок плейлистів та відео
- **reports** - скарги на відео
- **channel_strikes** - штрафи для каналів

**Детальна документація схеми:** [`docs/schema.md`](docs/schema.md)  
**Складні SQL-запити:** [`docs/queries.md`](docs/queries.md)

---

## Швидкий старт

### Передумови

- **Docker Desktop** та **Docker Compose** встановлені
- **Git**
- **Python 3.11+** (тільки для локальної розробки без Docker)
- **uv** - менеджер пакетів Python

### Крок 1: Клонування репозиторію

```bash
git clone https://github.com/Mr-Chekaut-Dungeon-IM-42/databases-2025-yeahtube.git
cd databases-2025-yeahtube
```

### Крок 2: Налаштування змінних оточення

**1. Скопіюйте приклад конфігурації:**

```bash
cp .env.example .env
```

**2. Відредагуйте файл `.env`:**

```env
DB_URL=postgresql://admin:password@postgres:5432/yeahtube
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**3. Підключення до бази даних:**

- **Для Docker (рекомендовано):** Використовуйте ім'я сервісу `postgres`
- **Для локальної розробки:** Використовуйте `localhost`

### Крок 3: Запуск через Docker (рекомендовано)

```bash
# Запуск контейнерів (PostgreSQL + pgAdmin)
docker compose up -d

# Перевірка логів
docker compose logs -f app
```

**Доступ до застосунку:**

- **API сервер:** `http://localhost:8000`
- **API документація (Swagger):** `http://localhost:8000/docs`
- **pgAdmin (UI для бази даних):** `http://localhost:5050`
  - Email: `admin@yeahtube.com`
  - Пароль: `admin`

### Крок 4: Локальна розробка

```bash
1. docker compose watch

2. uv sync

3. source .venv/bin/activate  # Linux/macOS
# або
.venv\Scripts\activate  # Windows

4. make migrate-upgrade-head

5. make populate

```

---

## Запуск тестів

### Автоматизоване тестування

Запуск всіх тестів у ізольованому Docker-оточенні.

```bash
# Перший запуск - створення тестової бази
docker compose up test_db -d

# Запуск тестів
make test

# Запуск конкретного файлу
pytest tests/test_admin.py

```

## Структура проєкту

```
databases-2025-yeahtube/
├── app/
│   ├── alembic/                # Міграції бази даних
│   │   └── versions/           # Файли міграцій
│   ├── db/
│   │   ├── models.py           # SQLAlchemy моделі
│   │   └── session.py          # Конфігурація сесії БД
│   ├── routers/
│   │   ├── admin.py            # Ендпоінти адміністратора
│   │   ├── auth.py             # Аутентифікація (JWT)
│   │   ├── channel.py          # Управління каналами
│   │   ├── user.py             # Управління користувачами
│   │   └── video.py            # Управління відео
│   ├── schemas/
│   │   └── schemas.py          # Pydantic схеми
│   ├── utils/
│   │   ├── auth.py             # Утиліти аутентифікації
│   │   └── populate.py         # Скрипт наповнення БД
│   ├── main.py                 # Головний файл FastAPI
│   ├── dependencies.py         # Залежності для роутерів
│   └── alembic.ini             # Конфігурація Alembic
│
├── tests/
│   ├── conftest.py             # Fixtures для тестів
│   ├── test_admin.py           # Тести адміністратора
│   └── test_user.py            # Тести користувачів
│
├── docs/
│   ├── schema.md               # Документація схеми БД
│   └── queries.md              # Документація складних запитів
│
├── compose.yml                 # Docker Compose конфігурація
├── Dockerfile                  # Docker образ
├── pyproject.toml              # Конфігурація проєкту та залежності
├── uv.lock                     # Lock-файл залежностей
└── README.md                   # Ця документація
```

---

## Приклади використання API

### Реєстрація користувача

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Вхід (отримання JWT токену)

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

Відповідь:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Створення каналу

```bash
curl -X POST "http://localhost:8000/channels/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Reviews Channel",
    "description": "Reviews of latest tech gadgets"
  }'
```

### Завантаження відео

```bash
curl -X POST "http://localhost:8000/videos/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Video",
    "description": "Introduction to my channel",
    "channel_id": 1,
    "video_url": "https://example.com/video.mp4"
  }'
```

### Перегляд рекомендацій (персоналізовані)

```bash
curl -X GET "http://localhost:8000/videos/recommendations?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Адміністративні операції

**Деактивація відео (тільки для модераторів):**

```bash
curl -X PUT "http://localhost:8000/admin/videos/123/deactivate" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Порушення правил спільноти"
  }'
```

**Додавання штрафу каналу:**

```bash
curl -X POST "http://localhost:8000/admin/channels/5/strikes" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Повторне порушення правил",
    "severity": "major"
  }'
```

**Аналітика проблемних каналів:**

```bash
curl -X GET "http://localhost:8000/admin/analytics/problematic-channels?min_reports=5" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

---

## Інструкції до міграцій

### Застосування всіх міграцій

```bash
make migrate-upgrade-head
```

### Створення нової міграції

```bash
make generate-migration message="test_for_migration"
```

### Відкат міграції

```bash
make migrate-downgrade-one
```

## Наповнення бази тестовими даними

```bash
make populate
```

Скрипт створить:
- 10 користувачів (включаючи 1 модератора)
- 5 каналів
- 20 відео
- 50 коментарів
- 100 переглядів
- Підписки, плейлисти та скарги

---

## Документація

- **Схема бази даних:** [`docs/schema.md`](docs/schema.md) - повний опис всіх таблиць, зв'язків та дизайн-рішень
- **Складні запити:** [`docs/queries.md`](docs/queries.md) - документація аналітичних SQL-запитів з поясненнями
- **API документація:** `http://localhost:8000/docs` (Swagger UI)
- **Swagger:** `http://localhost:8000/docs` (альтернативний інтерфейс API документації)