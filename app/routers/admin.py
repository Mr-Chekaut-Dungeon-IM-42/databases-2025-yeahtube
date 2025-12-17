from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.models import Channel, Report, User, Video
from app.db.session import DBDep

router = APIRouter(tags=["admin"], prefix="/admin")


@router.patch("/video/{video_id}/deactivate")
async def deactivate_video(video_id: int, db: DBDep):
    video = db.execute(select(Video).where(Video.id == video_id)).scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not video.is_active:
        raise HTTPException(status_code=400, detail="Video is already inactive")
    
    video.is_active = False
    db.commit()
    db.refresh(video)
    
    return {
        "message": "Video deactivated successfully",
        "video_id": video.id,
        "title": video.title,
        "is_active": video.is_active
    }


@router.patch("/video/{video_id}/demonetize")
async def demonetize_video(video_id: int, db: DBDep):
    video = db.execute(select(Video).where(Video.id == video_id)).scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not video.is_monetized:
        raise HTTPException(status_code=400, detail="Video is already not monetized")
    
    video.is_monetized = False
    db.commit()
    db.refresh(video)
    
    return {
        "message": "Video demonetized successfully",
        "video_id": video.id,
        "title": video.title,
        "is_monetized": video.is_monetized
    }


@router.post("/user/{user_id}/ban")
async def ban_user(user_id: int, db: DBDep):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_banned:
        raise HTTPException(status_code=400, detail="User is already banned")
    
    user.is_banned = True
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User banned successfully",
        "user_id": user.id,
        "username": user.username,
        "is_banned": user.is_banned
    }


@router.post("/channel/{channel_id}/strike")
async def add_channel_strike(channel_id: int, db: DBDep):
    channel = db.execute(
        select(Channel).where(Channel.id == channel_id)
    ).scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.strikes += 1
    db.commit()
    db.refresh(channel)
    
    penalty_message = ""
    if channel.strikes >= 3:
        penalty_message = "Channel has reached 3 strikes and may face additional penalties."
    
    return {
        "message": f"Strike added to channel successfully. {penalty_message}",
        "channel_id": channel.id,
        "channel_name": channel.name,
        "strikes": channel.strikes
    }


@router.get("/reports")
async def get_all_reports(
    db: DBDep,
    resolved: bool | None = None,
    skip: int = 0,
    limit: int = 50
):
    query = select(Report)
    
    if resolved is not None:
        query = query.where(Report.is_resolved == resolved)
    
    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
    
    reports = db.execute(query).scalars().all()
    
    return {
        "reports": [
            {
                "id": report.id,
                "reason": report.reason,
                "created_at": report.created_at,
                "is_resolved": report.is_resolved,
                "reporter_id": report.reporter_id,
                "video_id": report.video_id
            }
            for report in reports
        ],
        "count": len(reports),
        "skip": skip,
        "limit": limit
    }


@router.patch("/report/{report_id}/resolve")
async def resolve_report(report_id: int, db: DBDep):
    report = db.execute(
        select(Report).where(Report.id == report_id)
    ).scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.is_resolved:
        raise HTTPException(status_code=400, detail="Report is already resolved")
    
    report.is_resolved = True
    db.commit()
    db.refresh(report)
    
    return {
        "message": "Report resolved successfully",
        "report_id": report.id,
        "is_resolved": report.is_resolved,
        "video_id": report.video_id
    }

