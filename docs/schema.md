# Схема бази даних YeahTube

## Діаграма сутність-зв'язок (ERD)

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     Users       │         │    Channels     │         │     Videos      │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │────┬───>│ id (PK)         │────┬───>│ id (PK)         │
│ username        │    │    │ name            │    │    │ title           │
│ email           │    │    │ created_at      │    │    │ description     │
│ hashed_password │    │    │ owner_id (FK)   │<───┘    │ uploaded_at     │
│ created_at      │    │    └─────────────────┘         │ is_active       │
│ is_moderator    │    │                                 │ is_monetized    │
│ is_deleted      │    │    ┌─────────────────┐         │ channel_id (FK) │
│ is_banned       │    │    │ Subscriptions   │         └─────────────────┘
└─────────────────┘    │    ├─────────────────┤                 │
         │             └───>│ user_id (FK,PK) │                 │
         │                  │ channel_id(FK,PK)│                │
         │                  │ is_active       │                 │
         │                  └─────────────────┘                 │
         │                           │                          │
         │                           │                          │
         │                  ┌─────────────────┐                 │
         │                  │ PaidSubscription│                 │
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ active_since    │                 │
         │                  │ active_to       │                 │
         │                  │ tier            │                 │
         │                  │ sub_user_id (FK)│                 │
         │                  │ sub_channel(FK) │                 │
         │                  └─────────────────┘                 │
         │                                                      │
         │                  ┌─────────────────┐                 │
         ├─────────────────>│    Comments     │<────────────────┤
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ comment_text    │                 │
         │                  │ commented_at    │                 │
         │                  │ user_id (FK)    │                 │
         │                  │ video_id (FK)   │                 │
         │                  └─────────────────┘                 │
         │                                                      │
         │                  ┌─────────────────┐                 │
         ├─────────────────>│      Views      │<────────────────┤
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ watched_at      │                 │
         │                  │ watch_duration  │                 │
         │                  │ user_id (FK)    │                 │
         │                  │ video_id (FK)   │                 │
         │                  └─────────────────┘                 │
         │                                                      │
         │                  ┌─────────────────┐                 │
         ├─────────────────>│     Reports     │<────────────────┤
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ reason          │                 │
         │                  │ created_at      │                 │
         │                  │ is_resolved     │                 │
         │                  │ reporter_id (FK)│                 │
         │                  │ video_id (FK)   │                 │
         │                  └─────────────────┘                 │
         │                                                      │
         │                  ┌─────────────────┐                 │
         ├─────────────────>│    Playlists    │                 │
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ name            │                 │
         │                  │ created_at      │                 │
         │                  │ author_id (FK)  │                 │
         │                  └─────────────────┘                 │
         │                          │                           │
         │                          │                           │
         │                  ┌─────────────────┐                 │
         │                  │ PlaylistVideo   │<────────────────┘
         │                  ├─────────────────┤
         │                  │ playlist_id(FK,PK)│
         │                  │ video_id (FK,PK)│
         │                  └─────────────────┘
         │
         │                  ┌─────────────────┐
         └─────────────────>│ ChannelStrikes  │
                            ├─────────────────┤
                            │ id (PK)         │
                            │ issued_at       │
                            │ duration        │
                            │ video_id (FK)   │
                            │ channel_id (FK) │
                            └─────────────────┘
```

## Опис таблиць

### Таблиця: users

Призначення: Зберігає інформацію про облікові записи користувачів платформи.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор користувача |
| username | VARCHAR(32) | UNIQUE, NOT NULL | Унікальне ім'я користувача |
| email | VARCHAR(64) | UNIQUE, NOT NULL | Email адреса користувача |
| hashed_password | VARCHAR(255) | NOT NULL | Хешований пароль для аутентифікації |
| created_at | DATE | NOT NULL | Дата реєстрації облікового запису |
| is_moderator | BOOLEAN | NOT NULL, DEFAULT FALSE | Флаг адміністраторських прав |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Флаг м'якого видалення |
| is_banned | BOOLEAN | NOT NULL, DEFAULT FALSE | Флаг блокування користувача |

Індекси:
- PRIMARY KEY на id
- UNIQUE INDEX на username
- UNIQUE INDEX на email

Зв'язки:
- Один-до-багатьох з channels (користувач може мати кілька каналів)
- Один-до-багатьох з comments (користувач може залишати коментарі)
- Один-до-багатьох з views (користувач переглядає відео)
- Один-до-багатьох з reports (користувач може створювати скарги)
- Один-до-багатьох з subscriptions (користувач може підписуватись на канали)
- Один-до-багатьох з playlists (користувач може створювати плейлисти)

### Таблиця: channels

Призначення: Зберігає інформацію про канали контент-креаторів.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор каналу |
| name | VARCHAR(32) | NOT NULL | Назва каналу |
| created_at | DATE | NOT NULL | Дата створення каналу |
| owner_id | INTEGER | NOT NULL, FOREIGN KEY(users.id) | Власник каналу |

Індекси:
- PRIMARY KEY на id

Зв'язки:
- Багато-до-одного з users (канал належить одному користувачу)
- Один-до-багатьох з videos (канал містить багато відео)
- Один-до-багатьох з subscriptions (на канал можуть підписуватись)
- Один-до-багатьох з channel_strikes (канал може мати штрафи)

### Таблиця: videos

Призначення: Зберігає інформацію про завантажені відео.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор відео |
| title | TEXT | NOT NULL, CHECK(length <= 128) | Назва відео |
| description | TEXT | NULL, CHECK(length <= 256) | Опис відео |
| uploaded_at | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата завантаження |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Чи активне відео |
| is_monetized | BOOLEAN | NOT NULL, DEFAULT FALSE | Чи монетизоване відео |
| channel_id | INTEGER | NOT NULL, FOREIGN KEY(channels.id) | Канал, що опублікував відео |

Обмеження:
- CHECK: length(title) <= 128
- CHECK: length(description) <= 256

Зв'язки:
- Багато-до-одного з channels (відео належить одному каналу)
- Один-до-багатьох з comments (відео може мати коментарі)
- Один-до-багатьох з views (відео можуть переглядати)
- Один-до-багатьох з reports (на відео можуть скаржитись)

### Таблиця: comments

Призначення: Зберігає коментарі користувачів до відео.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор коментаря |
| comment_text | TEXT | NOT NULL, CHECK(length <= 2048) | Текст коментаря |
| commented_at | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата публікації коментаря |
| user_id | INTEGER | NOT NULL, FOREIGN KEY(users.id) | Автор коментаря |
| video_id | INTEGER | NOT NULL, FOREIGN KEY(videos.id) | Відео, до якого залишено коментар |

Обмеження:
- CHECK: length(comment_text) <= 2048

Зв'язки:
- Багато-до-одного з users (коментар написаний користувачем)
- Багато-до-одного з videos (коментар належить до відео)

### Таблиця: views

Призначення: Зберігає інформацію про перегляди відео користувачами.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор перегляду |
| watched_at | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата перегляду |
| watch_duration | INTERVAL | NULL, CHECK(watch_duration >= '0') | Тривалість перегляду |
| user_id | INTEGER | NOT NULL, FOREIGN KEY(users.id) | Користувач, що переглянув |
| video_id | INTEGER | NOT NULL, FOREIGN KEY(videos.id) | Переглянуте відео |

Обмеження:
- CHECK: watch_duration >= '0'::interval

Зв'язки:
- Багато-до-одного з users (перегляд зроблений користувачем)
- Багато-до-одного з videos (перегляд відео)

### Таблиця: reports

Призначення: Зберігає скарги користувачів на відео.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор скарги |
| reason | TEXT | NOT NULL, CHECK(length <= 512) | Причина скарги |
| created_at | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата створення скарги |
| is_resolved | BOOLEAN | NOT NULL, DEFAULT FALSE | Чи розглянута скарга |
| reporter_id | INTEGER | NOT NULL, FOREIGN KEY(users.id) | Користувач, що створив скаргу |
| video_id | INTEGER | NOT NULL, FOREIGN KEY(videos.id) | Відео, на яке скаржаться |

Обмеження:
- CHECK: length(reason) <= 512

Зв'язки:
- Багато-до-одного з users (скарга створена користувачем)
- Багато-до-одного з videos (скарга на відео)

### Таблиця: subscription

Призначення: Зберігає підписки користувачів на канали.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY(users.id) | Користувач-підписник |
| channel_id | INTEGER | PRIMARY KEY, FOREIGN KEY(channels.id) | Канал підписки |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Чи активна підписка |

Індекси:
- COMPOSITE PRIMARY KEY на (user_id, channel_id)

Зв'язки:
- Багато-до-одного з users
- Багато-до-одного з channels
- Один-до-багатьох з paid_subscriptions

### Таблиця: paid_subscriptions

Призначення: Зберігає інформацію про платні підписки.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор |
| active_since | DATETIME | NOT NULL, DEFAULT NOW() | Початок підписки |
| active_to | DATETIME | NULL | Закінчення підписки |
| tier | ENUM | NOT NULL | Рівень підписки (BRONZE, SILVER, GOLD, DIAMOND) |
| sub_user_id | INTEGER | NOT NULL, FOREIGN KEY(subscription.user_id) | Користувач підписки |
| sub_channel_id | INTEGER | NOT NULL, FOREIGN KEY(subscription.channel_id) | Канал підписки |

Зв'язки:
- Багато-до-одного з subscription (через composite foreign key)

### Таблиця: playlists

Призначення: Зберігає користувацькі плейлисти.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор плейлиста |
| name | VARCHAR(64) | NOT NULL | Назва плейлиста |
| created_at | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата створення |
| author_id | INTEGER | NOT NULL, FOREIGN KEY(users.id) | Автор плейлиста |

Зв'язки:
- Багато-до-одного з users (плейлист створений користувачем)
- Один-до-багатьох з playlist_video (відео в плейлисті)

### Таблиця: playlist_video

Призначення: Проміжна таблиця для зв'язку плейлистів з відео (Many-to-Many).

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| playlist_id | INTEGER | PRIMARY KEY, FOREIGN KEY(playlists.id) | Плейлист |
| video_id | INTEGER | PRIMARY KEY, FOREIGN KEY(videos.id) | Відео |

Індекси:
- COMPOSITE PRIMARY KEY на (playlist_id, video_id)

Зв'язки:
- Багато-до-одного з playlists
- Багато-до-одного з videos

### Таблиця: channel_strikes

Призначення: Зберігає штрафи/порушення для каналів.

Стовпці:
| Стовпець | Тип | Обмеження | Опис |
|----------|-----|-----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Унікальний ідентифікатор штрафу |
| issued_at | DATETIME | NOT NULL, DEFAULT NOW() | Час видачі штрафу |
| duration | INTERVAL | NOT NULL | Тривалість штрафу |
| video_id | INTEGER | NULL, FOREIGN KEY(videos.id) | Відео-причина (якщо є) |
| channel_id | INTEGER | NOT NULL, FOREIGN KEY(channels.id) | Канал, що отримав штраф |

Зв'язки:
- Багато-до-одного з channels (штраф для каналу)
- Багато-до-одного з videos (опціонально - відео-причина)

## Рішення щодо дизайну

## Стратегія індексування

База даних використовує індекси для оптимізації найчастіших запитів. Всі індекси створені на рівні ORM (SQLAlchemy) через параметр `index=True` у визначенні колонок моделей.

### Реалізовані індекси

#### 1. users
```sql
CREATE INDEX ix_users_is_deleted ON users(is_deleted);
```
- Призначення: Фільтрація активних/видалених користувачів
- Використання: Всі запити виключають is_deleted=TRUE
- Тип: B-tree (за замовчуванням)

#### 2. channels
```sql
CREATE INDEX ix_channels_owner_id ON channels(owner_id);
```
- Призначення: Пошук каналів конкретного користувача
- Використання: Запити "всі канали користувача X"
- Зовнішній ключ: users(id)

#### 3. videos
```sql
CREATE INDEX ix_videos_is_active ON videos(is_active);
CREATE INDEX ix_videos_channel_id ON videos(channel_id);
```
- ix_videos_is_active: Фільтрація активних/деактивованих відео (важливо для модерації)
- ix_videos_channel_id: Пошук всіх відео каналу (для сторінок каналів)

#### 4. comments
```sql
CREATE INDEX ix_comments_commented_at ON comments(commented_at);
CREATE INDEX ix_comments_video_id ON comments(video_id);
CREATE INDEX ix_comments_user_id ON comments(user_id);
```
- ix_comments_commented_at: Сортування коментарів за датою (нові зверху)
- ix_comments_video_id: Завантаження всіх коментарів відео
- ix_comments_user_id: Пошук коментарів конкретного користувача

#### 5. views
```sql
CREATE INDEX ix_views_watched_at ON views(watched_at);
CREATE INDEX ix_views_user_id ON views(user_id);
```
- ix_views_watched_at: Аналітика переглядів за періодами (день/тиждень/рік)
- ix_views_user_id: Історія переглядів користувача, рекомендації

#### 6. reports
```sql
CREATE INDEX ix_reports_is_resolved ON reports(is_resolved);
CREATE INDEX ix_reports_reporter_id ON reports(reporter_id);
CREATE INDEX ix_reports_video_id ON reports(video_id);
```
- ix_reports_is_resolved: Фільтр активних скарг для модераторів
- ix_reports_reporter_id: Аналіз проблемних користувачів (багато скарг)
- ix_reports_video_id: Всі скарги на конкретне відео

### Composite індекси (рекомендації для майбутнього)

Наразі не реалізовані, але можуть покращити продуктивність складних запитів:

```sql
-- Для рекомендаційної системи
CREATE INDEX idx_views_user_video ON views(user_id, video_id);

-- Для аналітики переглядів користувача за період
CREATE INDEX idx_views_user_watched ON views(user_id, watched_at);

-- Для пошуку нерозглянутих скарг на відео
CREATE INDEX idx_reports_video_resolved ON reports(video_id, is_resolved);

-- Для пошуку активних відео каналу
CREATE INDEX idx_videos_channel_active ON videos(channel_id, is_active);
```

### Обґрунтування індексів

1. Зовнішні ключі: Всі FK колонки мають індекси для прискорення JOIN операцій
2. Фільтраційні поля: is_active, is_deleted, is_resolved часто використовуються у WHERE
3. Дати: watched_at, commented_at використовуються для сортування та фільтрації за періодами
4. Unique constraints: username, email автоматично мають унікальні індекси



## Рішення щодо дизайну

### Нормалізація

База даних спроектована у третій нормальній формі (3НФ):

1. Всі таблиці мають первинні ключі
2. Відсутні повторювані групи (всі багатозначні атрибути винесені в окремі таблиці)
3. Всі неключові атрибути залежать від первинного ключа
4. Відсутні транзитивні залежності

Нормалізація реалізована через:
- Замість зберігання списку підписок в таблиці users, створена окрема таблиця subscription
- Платні підписки винесені в окрему таблиць paid_subscriptions замість додавання полів до subscription
- Зв'язок Many-to-Many між плейлистами та відео реалізовано через проміжну таблицю playlist_video

### М'яке видалення

Реалізували soft delete для користувачів:
- Поле is_deleted у таблиці users
- Видалені користувачі залишаються в базі для збереження історії та цілісності зв'язків
- Запити фільтрують видалених користувачів через WHERE is_deleted = FALSE

### Каскадне видалення

Налаштовано CASCADE для підтримки референційної цілісності:
- При видаленні користувача видаляються його канали, коментарі, перегляди
- При видаленні каналу видаляються його відео
- При видаленні відео видаляються пов'язані коментарі, перегляди, записи в плейлистах

### Обмеження цілісності

CHECK constraints забезпечують валідність даних:
- Обмеження довжини текстових полів
- Обмеження на позитивну тривалість перегляду
- Enum типи для обмеження можливих значень (tier у paid_subscriptions)

### Компроміси

1. Denormalization для продуктивності:
   - is_active у subscription дублюється логікою з paid_subscriptions, але спрощує запити

2. Відсутність історії змін:
   - Не зберігається історія редагувань коментарів або відео
   - За потреби можна додати окремі audit таблиці

3. Проста модель штрафів:
   - channel_strikes зберігає тільки факт штрафу, не деталі розгляду
   - При масштабуванні може знадобитись більш складна система модерації
