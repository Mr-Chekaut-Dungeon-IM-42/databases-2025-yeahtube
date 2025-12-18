from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import and_, delete, func, select, update

from app.db.models import (
    Channel,
    ChannelStrike,
    PaidSubscription,
    Subscription,
    User,
    Video,
    View,
)
from app.db.session import DBDep
from app.schemas.schemas import (
    ChannelInfoBrief,
    ChannelInfoFull,
    ChannelRevenue,
    VideoInfo,
)

router = APIRouter(tags=["channel"], prefix="/channel")

# GET Channel total viewcount
# GET Channel subscribers
# POST Create channel
# PATCH Rename channel
# DELETE Delete channel
#
# OLAP: Total revenue from monthly paid subscriptions
# OLAP: Strike count for channel, excluding the ones that have been expired.
# NOTE: may be too easy? ^


@router.get("/{channel_id}/info")
async def channel_fullinfo(channel_id: int, db: DBDep) -> ChannelInfoFull:
    res = db.execute(
        select(
            Channel.id,
            Channel.name,
            User.id,
            User.username,
            func.count(Subscription.user_id).label("subscriber_count"),
        )
        .join(User, Channel.owner_id == User.id)
        .outerjoin(
            Subscription,
            and_(Subscription.channel_id == Channel.id, Subscription.is_active),
        )
        .where(Channel.id == channel_id)
        .group_by(Channel.id, Channel.name, User.id, User.username)
    ).first()

    if not res:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Channel not found")
    ch_id, ch_name, creator_id, creator_name, subs = res

    v_query = (
        select(Video.id, Video.title, func.count(View.user_id))
        .select_from(Video)
        .outerjoin(View, Video.id == View.video_id)
        .where(Video.channel_id == channel_id)
        .group_by(Video.id, Video.title)
    )
    vresult = db.execute(v_query).all()
    videos = [
        VideoInfo(id=vid, title=title, views=views) for (vid, title, views) in vresult
    ]
    total_views = sum(v.views for v in videos)

    now = datetime.now(UTC)
    q = (
        select(func.count())
        .select_from(ChannelStrike)
        .where(
            ChannelStrike.channel_id == channel_id,
            (ChannelStrike.issued_at + ChannelStrike.duration) > now,
        )
    )
    strike_count = db.scalar(q) or 0

    return ChannelInfoFull(
        id=ch_id,
        name=ch_name,
        owner_id=creator_id,
        owner_name=creator_name,
        total_views=total_views,
        subscribers=subs,
        strike_count=strike_count,
        videos=videos,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_channel(name: str, db: DBDep, user_id: int) -> ChannelInfoFull:
    creator = db.get(User, user_id)
    if not creator:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Target user not found")
    ch = Channel(name=name, owner_id=user_id, created_at=datetime.now(UTC).date())

    db.add(ch)
    db.commit()
    db.refresh(ch)

    return ChannelInfoFull(
        id=ch.id,
        name=ch.name,
        owner_id=creator.id,
        owner_name=creator.username,
        subscribers=0,
        total_views=0,
        strike_count=0,
        videos=[],
    )


@router.patch("/{channel_id}/rename", status_code=status.HTTP_200_OK)
def rename_channel(
    channel_id: int,
    new_name: str,
    db: DBDep,
    user_id: int,
):
    owner = db.get(User, user_id)
    if not owner:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    try:
        channel_id, channel_name, strikes = (
            db.execute(
                update(Channel)
                .values(name=new_name)
                .where(Channel.id == channel_id, Channel.owner_id == user_id)
                .returning(
                    Channel.id,
                    Channel.name,
                    func.count(Channel.channel_strikes),
                )
            )
            .one()
            .t
        )
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized to rename")

    db.commit()
    return ChannelInfoBrief(
        id=channel_id, name=channel_name, owner_username=owner.username, strikes=strikes
    )


@router.delete("/{channel_id}", status_code=status.HTTP_200_OK)
def delete_channel(channel_id: int, db: DBDep, user_id: int) -> ChannelInfoBrief:
    owner = db.get(User, user_id)
    if not owner:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    try:
        channel_id, channel_name, strikes = (
            db.execute(
                delete(Channel)
                .where(Channel.id == channel_id, Channel.owner_id == user_id)
                .returning(
                    Channel.id,
                    Channel.name,
                    func.count(Channel.channel_strikes),
                )
            )
            .one()
            .t
        )
    except:
        raise
        # raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized to delete")

    db.commit()
    return ChannelInfoBrief(
        id=channel_id, name=channel_name, owner_username=owner.username, strikes=strikes
    )


@router.get("/{channel_id}/revenue", response_model=ChannelRevenue)
def channel_revenue(channel_id: int, db: DBDep) -> ChannelRevenue:
    channel = db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Channel not found")

    rows = db.execute(
        select(
            PaidSubscription.active_since,
            PaidSubscription.active_to,
            PaidSubscription.tier,
        ).join(
            Subscription,
            and_(
                PaidSubscription.sub_channel_id == Subscription.channel_id,
                Subscription.channel_id == channel_id,
            ),
        )
    ).all()
    now = datetime.now(UTC)
    total = 0.0
    for active_since, active_to, tier in rows:
        sub_start = active_since
        sub_end = active_to or (sub_start + timedelta(days=30))
        if active_to is None and sub_end > now:
            sub_end = now
        period = sub_end - sub_start
        months = int(period.days / 30) or 1
        total += float(tier.value) * months
    return ChannelRevenue(channel_id=channel_id, revenue_usd=f"{total:.2f}")
