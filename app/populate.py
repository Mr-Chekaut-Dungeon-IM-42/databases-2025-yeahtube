import random
from datetime import date, datetime

from db.models import (
    Channel,
    ChannelStrike,
    Comment,
    PaidSubscription,
    PaidSubTier,
    Playlist,
    PlaylistVideo,
    Subscription,
    User,
    Video,
    View,
)
from db.session import SessionLocal
from faker import Faker
from sqlalchemy.orm import Session
from utils.auth import get_password_hash


def create_test_data(session: Session) -> None:
    fake = Faker()
    fake.unique.clear()

    session.query(View).delete()
    session.query(Subscription).delete()
    session.query(PlaylistVideo).delete()
    session.query(Playlist).delete()
    session.query(Comment).delete()
    session.query(Video).delete()
    session.query(Channel).delete()
    session.query(User).delete()

    users = []
    for _ in range(500):
        username = fake.unique.user_name()
        email = fake.unique.email()
        created_at = fake.date_between(
            start_date=date(2020, 1, 1), end_date=date.today()
        )
        is_moderator = fake.boolean(chance_of_getting_true=5)  # 5% moderators
        user = User(
            username=username,
            email=email,
            created_at=created_at,
            is_moderator=is_moderator,
        )
        users.append(user)

    session.add_all(users)

    channels = []
    for user in users:
        num_channels = fake.random_int(0, 3)
        for _ in range(num_channels):
            channel_name = fake.company()[:32]
            created_at = fake.date_between(
                start_date=user.created_at, end_date=date.today()
            )
            channel = Channel(name=channel_name, created_at=created_at, owner=user)
            channels.append(channel)

    session.add_all(channels)

    videos = []
    for channel in channels:
        num_videos = fake.random_int(1, 10)
        for _ in range(num_videos):
            title = fake.sentence(nb_words=5)[:128]
            description = fake.text(max_nb_chars=200) if fake.boolean() else None
            uploaded_at = fake.date_between(
                start_date=channel.created_at, end_date=date.today()
            )
            video = Video(
                title=title,
                description=description,
                uploaded_at=uploaded_at,
                channel=channel,
            )
            videos.append(video)

    session.add_all(videos)

    strikes = [
        ChannelStrike(
            issued_at=fake.date_time_this_decade(),
            duration=fake.time_delta(end_datetime="+90d"),
            channel=random.choice(channels),
            video=random.choice(videos) if fake.boolean(80) else None,
        )
        for _ in range(len(channels) * 3)
    ]

    session.add_all(strikes)

    comments = []
    for _ in range(2000):
        user = fake.random_element(users)
        video = fake.random_element(videos)
        comment_text = fake.sentence(nb_words=10)[:2048]
        commented_at = fake.date_between(
            start_date=max(user.created_at, video.uploaded_at), end_date=date.today()
        )
        comment = Comment(
            comment_text=comment_text, commented_at=commented_at, user=user, video=video
        )
        comments.append(comment)

    session.add_all(comments)

    playlists = []
    for user in users:
        num_playlists = fake.random_int(0, 2)
        for _ in range(num_playlists):
            name = fake.sentence(nb_words=3)[:64]
            created_at = fake.date_between(
                start_date=user.created_at, end_date=date.today()
            )
            playlist = Playlist(name=name, created_at=created_at, author=user)
            playlists.append(playlist)

    session.add_all(playlists)

    playlist_entries = []
    for playlist in playlists:
        num_entries = fake.random_int(1, 10)
        selected_videos = fake.random_elements(videos, length=num_entries, unique=True)
        for video in selected_videos:
            pv = PlaylistVideo(playlist=playlist, video=video)
            playlist_entries.append(pv)

    session.add_all(playlist_entries)

    subscriptions = []
    TIERS = [
        PaidSubTier.BRONZE,
        PaidSubTier.SILVER,
        PaidSubTier.GOLD,
        PaidSubTier.DIAMOND,
    ]
    for user in users:
        num_subs = fake.random_int(0, 20)
        potential_channels = [c for c in channels if c.owner != user]
        if potential_channels:
            selected_channels = fake.random_elements(
                potential_channels,
                length=min(num_subs, len(potential_channels)),
                unique=True,
            )
            for channel in selected_channels:
                num_paid_subs = fake.random_int(0, 10)
                paid_sub_dates = [fake.date_time_this_decade(before_now=True)]
                for _ in range(num_paid_subs * 2 - 1):
                    paid_sub_dates.append(
                        fake.date_time_between(paid_sub_dates[-1], datetime.now())
                    )
                paid_subs = [
                    PaidSubscription(
                        active_since=since, active_to=to, tier=random.choice(TIERS)
                    )
                    for since, to in zip(paid_sub_dates[::2], paid_sub_dates[1::2])
                ]
                sub = Subscription(user=user, channel=channel, paid_subs=paid_subs)
                subscriptions.append(sub)

    session.add_all(subscriptions)

    views = []
    for user in users:
        num_views = fake.random_int(10, 100)
        selected_videos = fake.random_elements(
            videos, length=min(num_views, len(videos)), unique=True
        )
        for video in selected_videos:
            watched_at = fake.date_between(
                start_date=max(user.created_at, video.uploaded_at),
                end_date=date.today(),
            )
            watched_percentage = fake.pyfloat(min_value=0.0, max_value=1.0)
            reaction = fake.random_element(
                elements=[None, None, None, "Liked", "Disliked"]
            )

            view = View(
                user=user,
                video=video,
                watched_at=watched_at,
                watched_percentage=watched_percentage,
                reaction=reaction,
            )
            views.append(view)

    session.add_all(views)
    session.commit()


if __name__ == "__main__":
    create_test_data(get_session())
