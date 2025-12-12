# Інструкції до запуску

- Мати  встановлений `uv` і запущений postgres-сервер, доступний за адресою у
  змінній оточення `DB_URL`, або, за її відсутності,
  `postgresql://admin:password@localhost:5432/db_labs`.
- У директорії `lab6` прописати `uv sync`
- Активувати virtual environment: `. .venv/bin/activate` (для лінуксоїдів, на
  вінді венв активується через `.venv/bin/activate.bat` (або `.ps1` для
  PowerShell), чи якось так).
- Перейти у директорію src/: `cd src`
- Ініціалізувати початкову схему: `alembic upgrade 2c6c3c579839`
- Заповнити таблицю тестовими даними: `uv run src/populate.py`
- Вручну перевірити стан таблиці.
- Застосувати міграції: `alembic upgrade <rev>` для конкретної ревізії,
  `alembic upgrade head` для останньої.

# Хід виконання

## Стан після нульової міграції з початковими тестовими даними

Версія бази даних:
[`2c6c3c579839_init.py`](https://github.com/Mr-Chekaut-Dungeon-IM-42/databases-2025/blob/main/lab6/src/alembic/versions/2c6c3c579839_init.py)

Вигляд таблиці `subscription` після міграції:

```sql
db_labs=# select * from subscription;
 user_id | channel_id 
---------+------------
       3 |          2
       3 |          1
       2 |          1
(3 rows)
```

## Міграція №1: додавання поля у таблицю

Зміни у визначенні моделей:

```diff
 class Subscription(Base):
     __tablename__ = "subscription"
  
     user_id: Mapped[int] = mapped_column(
         Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
     )
     channel_id: Mapped[int] = mapped_column(
         Integer, ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True
     )
+    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

     user: Mapped[User] = relationship("User", back_populates="subscriptions")
     channel: Mapped[Channel] = relationship("Channel", back_populates="subscribers")
```

Версія бази даних:
[`5d339deb073c_add_premium_subscriptions.py`](https://github.com/Mr-Chekaut-Dungeon-IM-42/databases-2025/blob/main/lab6/src/alembic/versions/5d339deb073c_add_premium_subscriptions.py)

Вигляд таблиці `subscription` після міграції:

```sql
db_labs=# select * from subscription;
 user_id | channel_id | is_premium 
---------+------------+------------
       3 |          2 | f
       3 |          1 | f
       2 |          1 | f
(3 rows)
```

## Міграція №2: створення таблиці

Зміни у визначенні моделей:

```python
class Moderator(Base):
    __tablename__ = "moderators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped[User] = relationship("User", back_populates="moderators")
```

Ручні зміни у згенерованій міграції:

```python
op.bulk_insert(
    sa.Table("moderators", Base.metadata),
    [{"id": 1, "created_at": "2025-12-07", "user_id": 1}],
)
```

Версія бази даних:
[`ad14dc436a24_add_moderator_users.py`](https://github.com/Mr-Chekaut-Dungeon-IM-42/databases-2025/blob/main/lab6/src/alembic/versions/ad14dc436a24_add_moderator_users.py)

Вигляд таблиці `moderators` після міграції:

```sql
db_labs=# select * from moderators;
 id | created_at | user_id 
----+------------+---------
  1 | 2025-12-07 |       1
(1 row)
```

## Міграція №3: видалення таблиці

Зміни у визначенні моделей:

```diff
- class Playlist(Base):
-     __tablename__ = "playlists"
- 
-     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
-     name: Mapped[str] = mapped_column(String(64), nullable=False)
-     created_at: Mapped[str] = mapped_column(
-         Date, nullable=False, server_default=text("CURRENT_DATE")
-     )
-     author_id: Mapped[int] = mapped_column(
-         Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
-     )
- 
-     author: Mapped[User] = relationship("User", back_populates="playlists")
-     videos: Mapped[list["PlaylistVideo"]] = relationship(
-         "PlaylistVideo", back_populates="playlist", cascade="all, delete-orphan"
-     )
- 
- 
- class PlaylistVideo(Base):
-     __tablename__ = "playlist_video"
- 
-     playlist_id: Mapped[int] = mapped_column(
-         Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True
-     )
-     video_id: Mapped[int] = mapped_column(
-         Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
-     )
- 
-     playlist: Mapped[Playlist] = relationship("Playlist", back_populates="videos")
-     video: Mapped[Video] = relationship("Video", back_populates="playlist_entries")

...

 class Video(Base):
     __tablename__ = "videos"
     __table_args__ = (
         CheckConstraint("length(title) <= 128", name="ck_videos_title_length"),
         CheckConstraint(
             "length(description) <= 256", name="ck_videos_description_length"
         ),
     )
 
     ...
 
-     playlist_entries: Mapped[list["PlaylistVideo"]] = relationship(
-         "PlaylistVideo", back_populates="video", cascade="all, delete-orphan"
-     )

 class User(Base):
     __tablename__ = "users"
 
     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
     email: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
     created_at: Mapped[str] = mapped_column(Date, nullable=False)
 
     channels: Mapped[list["Channel"]] = relationship(
         "Channel", back_populates="owner", cascade="all, delete-orphan"
     )
     comments: Mapped[list["Comment"]] = relationship(
         "Comment", back_populates="user", cascade="all, delete-orphan"
     )
-     playlists: Mapped[list["Playlist"]] = relationship(
-         "Playlist", back_populates="author", cascade="all, delete-orphan"
-    )
     subscriptions: Mapped[list["Subscription"]] = relationship(
         "Subscription", back_populates="user", cascade="all, delete-orphan"
     )
     views: Mapped[list["View"]] = relationship(
         "View", back_populates="user", cascade="all, delete-orphan"
     )
```

Версія бази даних:
[`e3d90608cd2d_remove_playlists.py`](https://github.com/Mr-Chekaut-Dungeon-IM-42/databases-2025/blob/main/lab6/src/alembic/versions/e3d90608cd2d_remove_playlists.py)

Вигляд таблиці `playlists` після міграції:

```sql
db_labs=# select from playlists;
ERROR:  relation "playlists" does not exist
LINE 1: select from playlists;
                    ^
```
