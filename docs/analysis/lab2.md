# Lab 2 — Domain models, mapping, and 4-layer separation

Дата: **15 May 2026**

## 1) Що зроблено в цій лабораторній

### Архітектурне розділення на 4 шари

У проєкті виділено пакети:

- `app/presentation/` — HTTP/UI рівень (FastAPI routers + глобальні exception handlers)
- `app/application/` — use-cases (координація сценаріїв, робота через репозиторії/адаптери)
- `app/domain/` — доменна модель (DB-незалежні моделі, value objects, domain errors, factory, ports)
- `app/infrastructure/` — реалізація доступу до інфраструктури (ORM↔Domain mapping, адаптери, перевірки через SQLAlchemy)

Правило залежностей витримано в напрямку:

`Presentation -> Application -> Domain <- Infrastructure`

Тобто Domain не імпортує FastAPI/SQLAlchemy/ORM, а Presentation не «протікає» в Application.

### Доменні моделі незалежні від БД

Доменні моделі зроблені у `app/domain/models.py` (anemic domain model). Вони не прив’язані до SQLAlchemy моделей і не містять ORM-специфіки.

Для інваріантів використані value objects (`app/domain/value_objects.py`), наприклад:

- `Email`
- `BoundedText`
- `WatchedPercentage`

### Мапінг Domain ↔ ORM в Infrastructure

В `app/infrastructure/mappers/orm_domain.py` реалізовано конвертацію:

- ORM (SQLAlchemy models) → Domain (dataclasses)
- частково Domain → ORM

Це дозволяє ізолювати домен від структури БД.

### Domain Factory + DIP

Для створення доменних агрегатів (наприклад, користувача) використано **Domain Factory**: `app/domain/factories.py`.

Фабрика приймає залежність через інтерфейс (порт) `UserUniquenessChecker` (`app/domain/repositories.py`).

Інфраструктурна реалізація, яка робить складну інваріантну перевірку через БД — `SqlAlchemyUserUniquenessChecker` (`app/infrastructure/repositories/user_uniqueness.py`).

### Domain errors (без HTTP)

У `app/domain/errors.py` — доменні винятки, які не містять HTTP-кодів.

Presentation шар мапить ці винятки в HTTP відповіді через глобальні handlers: `app/presentation/exception_handlers.py`.

## 2) Чому обрано Anemic Domain Model

В ADR `docs/adr/0001-anemic-domain-model.md` зафіксовано рішення:

- Так простіше інтегруватися з існуючим проєктом, де логіка вже була розкидана між `repositories/*` і `services/*`.
- Немає великого обсягу складної бізнес-логіки всередині агрегатів.
- Інваріанти контролюються або value objects, або factory.

## 3) Як це допомагає замінювати БД / фреймворк

- **Заміна БД/ORM:** змінюється Infrastructure (репозиторії + мапінг). Domain і Application залишаються стабільними.
- **Заміна веб-фреймворку:** змінюється Presentation (routers/handlers), але Application і Domain не залежать від FastAPI.

## 4) Тести

Розділено:

- Unit тести домену і мапінгу (`tests/unit/*`)
- Unit тести Application (use-cases) без БД, через monkeypatch/mocks

Integration тести існують у `tests/integration/`, але їхній запуск потребує піднятої БД (Docker Compose).
