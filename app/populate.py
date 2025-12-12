from datetime import date

from sqlalchemy.orm import Session

# adjust the import path to where your models live
from db.models import (
    Channel,
    Comment,
    Playlist,
    PlaylistVideo,
    Subscription,
    User,
    Video,
    View,
)
from db.session import get_session


def create_test_data(session: Session) -> None:
    # Users
    alice = User(
        username="alice",
        email="alice@example.test",
        created_at=date(2021, 1, 1),
    )
    bob = User(
        username="bob",
        email="bob@example.test",
        created_at=date(2021, 2, 1),
    )
    carol = User(
        username="carol",
        email="carol@example.test",
        created_at=date(2021, 3, 1),
    )

    # Channels (owners are users)
    alice_channel = Channel(
        name="AliceChannel",
        created_at=date(2021, 1, 2),
        owner=alice,
    )
    bob_channel = Channel(
        name="BobChannel",
        created_at=date(2021, 2, 2),
        owner=bob,
    )

    # Videos
    vid1 = Video(
        title="Welcome to AliceChannel",
        description="Intro video",
        uploaded_at=date(2021, 1, 3),
        channel=alice_channel,
    )
    vid2 = Video(
        title="Deep dive: SQLAlchemy tips",
        description="A longer description but under limits",
        uploaded_at=date(2021, 1, 10),
        channel=alice_channel,
    )
    vid3 = Video(
        title="Bob's first upload",
        description=None,
        uploaded_at=date(2021, 2, 5),
        channel=bob_channel,
    )

    # Comments
    c1 = Comment(
        comment_text="Nice intro!",
        commented_at=date(2021, 1, 4),
        user=bob,
        video=vid1,
    )
    c2 = Comment(
        comment_text="Very helpful, thanks.",
        commented_at=date(2021, 1, 11),
        user=carol,
        video=vid2,
    )
    c3 = Comment(
        comment_text="Welcome Bob!",
        commented_at=date(2021, 2, 6),
        user=alice,
        video=vid3,
    )

    # Playlists
    p_alice = Playlist(
        name="Alice's favorites",
        created_at=date(2021, 1, 15),
        author=alice,
    )
    p_bob = Playlist(
        name="Bob's picks",
        created_at=date(2021, 2, 10),
        author=bob,
    )

    # Playlist entries (association objects)
    pv1 = PlaylistVideo(playlist=p_alice, video=vid1)
    pv2 = PlaylistVideo(playlist=p_alice, video=vid2)
    pv3 = PlaylistVideo(playlist=p_bob, video=vid3)
    pv4 = PlaylistVideo(playlist=p_bob, video=vid1)  # cross-channel inclusion

    # Subscriptions (user <-> channel)
    sub1 = Subscription(user=bob, channel=alice_channel)  # bob -> alice
    sub2 = Subscription(user=carol, channel=alice_channel)  # carol -> alice
    sub3 = Subscription(user=carol, channel=bob_channel)  # carol -> bob

    # Views (user <-> video)
    v1 = View(user=alice, video=vid3, watched_at=date(2021, 2, 6))
    v2 = View(user=bob, video=vid1, watched_at=date(2021, 1, 4))
    v3 = View(user=carol, video=vid2, watched_at=date(2021, 1, 12))
    v4 = View(user=carol, video=vid1, watched_at=date(2021, 1, 13))

    # Collect and persist
    session.add_all(
        [
            alice,
            bob,
            carol,
            alice_channel,
            bob_channel,
            vid1,
            vid2,
            vid3,
            c1,
            c2,
            c3,
            p_alice,
            p_bob,
            pv1,
            pv2,
            pv3,
            pv4,
            sub1,
            sub2,
            sub3,
            v1,
            v2,
            v3,
            v4,
        ]
    )
    session.commit()


if __name__ == "__main__":
    create_test_data(get_session())
