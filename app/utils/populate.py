import random
from datetime import date, datetime

from app.db.models import (
    Channel,
    ChannelStrike,
    Comment,
    PaidSubscription,
    PaidSubTier,
    Playlist,
    PlaylistVideo,
    Report,
    Subscription,
    User,
    Video,
    View,
)
from app.db.session import SessionLocal
from faker import Faker
from sqlalchemy.orm import Session
from app.utils.auth import get_password_hash


def create_test_data(session: Session) -> None:
    fake = Faker()
    fake.unique.clear()

    session.query(PaidSubscription).delete()
    session.query(ChannelStrike).delete()
    session.query(Report).delete()
    session.query(View).delete()
    session.query(Subscription).delete()
    session.query(PlaylistVideo).delete()
    session.query(Playlist).delete()
    session.query(Comment).delete()
    session.query(Video).delete()
    session.query(Channel).delete()
    session.query(User).delete()

    default_hashed_password = get_password_hash("testpassword123")

    users = []
    for _ in range(500):
        username = fake.unique.user_name()
        email = fake.unique.email()
        created_at = fake.date_between(
            start_date=date(2020, 1, 1), end_date=date.today()
        )
        is_moderator = fake.boolean(chance_of_getting_true=5)  # 5% moderators
        is_deleted = fake.boolean(chance_of_getting_true=3)  # 3% deleted users
        is_banned = fake.boolean(chance_of_getting_true=2)  # 2% banned users
        user = User(
            username=username,
            email=email,
            hashed_password=default_hashed_password,
            created_at=created_at,
            is_moderator=is_moderator,
            is_deleted=is_deleted,
            is_banned=is_banned,
        )
        users.append(user)

    session.add_all(users)
    session.commit()

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
    session.commit()

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
    session.commit()

    strikes = []
    for _ in range(len(channels) * 3):
        channel = random.choice(channels)
        issued_at = fake.date_time_this_decade()
        duration = fake.time_delta(end_datetime="+90d")
        video = random.choice(videos) if fake.boolean(80) else None

        strike = ChannelStrike(
            issued_at=issued_at,
            duration=duration,
            channel=channel,
            video=video,
        )
        strikes.append(strike)

    session.add_all(strikes)
    session.commit()

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
                is_active = fake.boolean(chance_of_getting_true=85)  # 85% active
                sub = Subscription(
                    user=user,
                    channel=channel,
                    is_active=is_active,
                )
                subscriptions.append(sub)

    session.add_all(subscriptions)
    session.commit()

    paid_subs = []
    for sub in subscriptions:
        # 30% chance of having paid subscription history
        if fake.boolean(chance_of_getting_true=30):
            num_paid_periods = fake.random_int(1, 5)

            for _ in range(num_paid_periods):
                active_since = fake.date_time_this_decade(before_now=True)
                # 70% chance it's expired, 30% chance it's still active
                if fake.boolean(chance_of_getting_true=70):
                    active_to = fake.date_time_between(active_since, datetime.now())
                else:
                    active_to = None  # Still active

                paid_sub = PaidSubscription(
                    active_since=active_since,
                    active_to=active_to,
                    tier=random.choice(TIERS),
                    sub_user_id=sub.user_id,
                    sub_channel_id=sub.channel_id,
                )
                paid_subs.append(paid_sub)

    session.add_all(paid_subs)

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
            reaction_choice = fake.random_int(0, 9)
            if reaction_choice < 6:
                reaction = None
            elif reaction_choice < 9:
                reaction = "Liked"
            else:
                reaction = "Disliked"

            view = View(
                user=user,
                video=video,
                watched_at=watched_at,
                watched_percentage=watched_percentage,
                reaction=reaction,
            )
            views.append(view)

    session.add_all(views)

    reports = []
    for _ in range(300):
        reporter = fake.random_element(users)
        video = fake.random_element(videos)
        reason = fake.sentence(nb_words=15)[:512]
        created_at = fake.date_between(
            start_date=max(reporter.created_at, video.uploaded_at),
            end_date=date.today(),
        )
        is_resolved = fake.boolean(chance_of_getting_true=40)
        report = Report(
            reason=reason,
            created_at=created_at,
            is_resolved=is_resolved,
            reporter=reporter,
            video=video,
        )
        reports.append(report)

    session.add_all(reports)
    session.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        create_test_data(session)
    finally:
        session.close()
