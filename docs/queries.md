# Складні SQL-запити YeahTube

## Запит 1: Персоналізовані рекомендації відео

Бізнес-питання: Які відео рекомендувати користувачу на основі його історії переглядів, підписок та загальної популярності?

SQL-запит:
```sql
WITH user_channel_views AS (
    SELECT 
        video.channel_id,
        COUNT(view.user_id) as channel_view_count
    FROM views AS view
    JOIN videos AS video ON view.video_id = video.id
    WHERE view.user_id = :user_id
    GROUP BY video.channel_id
),
subscriptions AS (
    SELECT channel_id
    FROM subscription
    WHERE user_id = :user_id
),
total_views AS (
    SELECT 
        video_id,
        COUNT(user_id) as total_view_count
    FROM views
    GROUP BY video_id
)
SELECT video.*
FROM videos AS video
LEFT JOIN user_channel_views 
    ON video.channel_id = user_channel_views.channel_id
LEFT JOIN total_views 
    ON video.id = total_views.video_id
LEFT JOIN subscriptions 
    ON video.channel_id = subscriptions.channel_id
ORDER BY 
    COALESCE(user_channel_views.channel_view_count, 0) DESC,
    (subscriptions.channel_id IS NOT NULL) DESC,
    COALESCE(total_views.total_view_count, 0) DESC
LIMIT :limit;
```

Пояснення:
- Використовує три Common Table Expressions (CTE) для підрахунку різних метрик
- user_channel_views рахує, скільки разів користувач переглядав відео з кожного каналу
- subscriptions містить канали, на які користувач підписаний
- total_views рахує загальну кількість переглядів кожного відео
- Сортування відбувається за пріоритетом: найбільше переглядів з каналів користувача, потім підписки, потім загальна популярність
- LEFT JOIN забезпечує включення всіх відео навіть без статистики
- COALESCE обробляє NULL значення, замінюючи їх на 0

Приклад виводу:
| id | title | channel_id | uploaded_at | is_active |
|----|-------|------------|-------------|-----------|
| 42 | Video User Loves | 5 | 2025-12-01 | true |
| 15 | Subscribed Content | 3 | 2025-12-10 | true |
| 88 | Trending Video | 12 | 2025-12-15 | true |

## Запит 2: Улюблений контент-креатор користувача

Бізнес-питання: Який канал користувач найбільше переглядав цього року?

SQL-запит:
```sql
SELECT 
    channel.name,
    COUNT(view.video_id) as view_count
FROM views AS view
JOIN videos AS video ON view.video_id = video.id
JOIN channels AS channel ON video.channel_id = channel.id
WHERE 
    view.user_id = :user_id
    AND EXTRACT(YEAR FROM view.watched_at) = :current_year
GROUP BY channel.id, channel.name
ORDER BY view_count DESC
LIMIT 1;
```

Пояснення:
- JOIN трьох таблиць для зв'язку користувача з каналами через відео
- EXTRACT(YEAR) фільтрує перегляди за поточний рік
- GROUP BY каналу для агрегації
- COUNT підраховує кількість переглядів
- ORDER BY + LIMIT 1 вибирає топ-канал

Приклад виводу:
| name | view_count |
|------|------------|
| Tech Reviews Channel | 45 |

## Запит 3: Аналітика проблемних користувачів

Бізнес-питання: Які користувачі створюють найбільше скарг (можливі спамери або тролі)?

SQL-запит:
```sql
SELECT 
    users.id,
    users.username,
    users.email,
    users.is_banned,
    COUNT(reports.id) as report_count
FROM users
JOIN reports ON users.id = reports.reporter_id
GROUP BY users.id, users.username, users.email, users.is_banned
HAVING COUNT(reports.id) >= :min_reports
ORDER BY report_count DESC
LIMIT :limit
OFFSET :skip;
```

Пояснення:
- JOIN users та reports для підрахунку скарг від кожного користувача
- GROUP BY для агрегації по користувачам
- HAVING фільтрує користувачів з певною мінімальною кількістю скарг
- Параметризований min_reports дозволяє налаштування порогу
- ORDER BY DESC сортує від найбільш проблемних
- LIMIT/OFFSET для пагінації

Приклад виводу:
| id | username | email | is_banned | report_count |
|----|----------|-------|-----------|--------------|
| 42 | spam_user | spam@test.com | false | 127 |
| 88 | troll123 | troll@test.com | true | 89 |
| 15 | angry_viewer | angry@test.com | false | 45 |

Використання: Адміністратори можуть швидко ідентифікувати підозрілих користувачів для перевірки або бану.

## Запит 4: Комплексна аналітика каналів з репутацією

Бізнес-питання: Які канали мають найбільше проблем (скарги, штрафи) та потребують уваги модераторів?

SQL-запит:
```sql
WITH strikes_count AS (
    SELECT 
        channel_id,
        COUNT(id) as strikes_count
    FROM channel_strikes
    GROUP BY channel_id
)
SELECT 
    channel.id as channel_id,
    channel.name as channel_name,
    COALESCE(strikes_count.strikes_count, 0) as strikes,
    users.username as owner_username,
    COUNT(reports.id) as total_reports,
    COUNT(DISTINCT video.id) as reported_videos_count,
    COUNT(DISTINCT reports.reporter_id) as unique_reporters,
    CAST(
        CAST(SUM(CAST(reports.is_resolved AS INTEGER)) AS FLOAT) 
        / COUNT(reports.id) * 100 
        AS NUMERIC(5,2)
    ) as resolved_percentage
FROM channels AS channel
JOIN videos AS video ON channel.id = video.channel_id
JOIN reports ON video.id = reports.video_id
JOIN users ON channel.owner_id = users.id
LEFT JOIN strikes_count ON channel.id = strikes_count.channel_id
GROUP BY 
    channel.id,
    channel.name,
    strikes_count.strikes_count,
    users.username
HAVING COUNT(reports.id) >= :min_reports
ORDER BY COUNT(reports.id) DESC
LIMIT :limit;
```

Пояснення:
- Підзапит strikes_count попередньо рахує штрафи для кожного каналу
- Основний запит об'єднує дані з 4 таблиць
- COUNT(DISTINCT) для точного підрахунку унікальних відео та репортерів
- Складне обчислення resolved_percentage через множинні CAST для підтримки різних типів даних
- COALESCE обробляє канали без штрафів
- HAVING фільтрує канали з мінімальною кількістю скарг
- LEFT JOIN для strikes дозволяє включити канали без штрафів

Приклад виводу:
| channel_id | channel_name | strikes | owner_username | total_reports | reported_videos_count | unique_reporters | resolved_percentage |
|------------|--------------|---------|----------------|---------------|----------------------|------------------|---------------------|
| 5 | Controversial Channel | 2 | user123 | 45 | 8 | 23 | 75.56 |
| 12 | Spam Videos | 3 | spammer | 38 | 15 | 19 | 50.00 |
| 8 | Borderline Content | 1 | creator88 | 22 | 5 | 14 | 90.91 |

Використання: Модератори можуть побачити повну картину проблемних каналів та визначити рівень ризику на основі кількості скарг, штрафів та відсотка розглянутих випадків.

Обчислення рівня ризику:
- HIGH: total_reports >= 10 OR strikes >= 2
- MEDIUM: total_reports >= 5 OR strikes >= 1
- LOW: інше

## Запит 5: Статистика переглядів користувача за рік

Бізнес-питання: Скільки відео переглянув користувач за поточний рік?

SQL-запит:
```sql
SELECT COUNT(video_id) as total_views
FROM views
WHERE 
    user_id = :user_id
    AND EXTRACT(YEAR FROM watched_at) = :current_year;
```

Пояснення:
- Простий агрегатний запит з фільтрацією
- EXTRACT(YEAR) ефективно фільтрує за рік без необхідності повного сканування дат
- COUNT підраховує всі перегляди

Індекс-рекомендація: Composite index на (user_id, watched_at) значно прискорить цей запит.

## Запит 6: Статистика реакцій користувача

Бізнес-питання: Скільки коментарів залишив користувач цього року?

SQL-запит:
```sql
SELECT COUNT(id) as total_reactions
FROM comments
WHERE 
    user_id = :user_id
    AND EXTRACT(YEAR FROM commented_at) = :current_year;
```

Пояснення:
- Аналогічний попередньому, але для коментарів
- Може бути розширений для включення лайків, дізлайків тощо

## Запит 7: Детальні скарги з інформацією про репортера та відео

Бізнес-питання: Які активні скарги потребують розгляду з повною інформацією?

SQL-запит:
```sql
SELECT 
    reports.id,
    reports.reason,
    reports.created_at,
    reports.is_resolved,
    users.id as reporter_id,
    users.username as reporter_username,
    videos.id as video_id,
    videos.title as video_title
FROM reports
JOIN users ON reports.reporter_id = users.id
JOIN videos ON reports.video_id = videos.id
WHERE reports.is_resolved = :resolved_filter
ORDER BY reports.created_at DESC
LIMIT :limit
OFFSET :skip;
```

Пояснення:
- JOIN трьох таблиць для повної інформації
- WHERE з параметром дозволяє фільтрувати розглянуті/нерозглянуті
- ORDER BY created_at DESC показує найсвіжіші скарги першими
- Пагінація через LIMIT/OFFSET

Приклад виводу:
| id | reason | created_at | is_resolved | reporter_id | reporter_username | video_id | video_title |
|----|--------|------------|-------------|-------------|-------------------|----------|-------------|
| 155 | Inappropriate content | 2025-12-18 | false | 42 | concerned_user | 888 | Controversial Video |
| 154 | Spam | 2025-12-18 | false | 23 | user123 | 777 | Spammy Content |

## Оптимізація запитів

### Рекомендовані індекси

1. Для рекомендацій:
```sql
CREATE INDEX idx_views_user_video ON views(user_id, video_id);
CREATE INDEX idx_videos_channel ON videos(channel_id);
```

2. Для аналітики за часом:
```sql
CREATE INDEX idx_views_user_watched ON views(user_id, watched_at);
CREATE INDEX idx_comments_user_commented ON comments(user_id, commented_at);
```

3. Для модерації:
```sql
CREATE INDEX idx_reports_resolved ON reports(is_resolved);
CREATE INDEX idx_reports_video ON reports(video_id);
```
