from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository
from app.schemas.schemas import (
    UserCredibilityResponse,
    UserDetailedResponse,
    UserUpdate,
    VideoResponse,
)


class UserService:
    @staticmethod
    def get_active_user_or_404(db: Session, user_id: int) -> UserDetailedResponse:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="User has been deleted"
            )
        return UserDetailedResponse.model_validate(user)

    @staticmethod
    def get_all_users(db: Session) -> list[UserDetailedResponse]:
        users = UserRepository.get_all_active(db)
        return [UserDetailedResponse.model_validate(u) for u in users]

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_data: UserUpdate
    ) -> UserDetailedResponse:
        user = UserRepository.get_by_id(db, user_id, for_update=True)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_deleted:
            raise HTTPException(status_code=410, detail="User has been deleted")

        if user_data.username and UserRepository.exists_by_username(
            db, user_data.username, user_id
        ):
            raise HTTPException(status_code=400, detail="Username already exists")
        if user_data.email and UserRepository.exists_by_email(
            db, user_data.email, user_id
        ):
            raise HTTPException(status_code=400, detail="Email already exists")

        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.is_moderator is not None:
            user.is_moderator = user_data.is_moderator

        db.commit()
        db.refresh(user)
        return UserDetailedResponse.model_validate(user)

    @staticmethod
    def soft_delete_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_deleted:
            raise HTTPException(status_code=410, detail="User already deleted")
        user.is_deleted = True
        db.commit()

    @staticmethod
    def get_recommendations(
        db: Session, user_id: int, limit: int
    ) -> list[VideoResponse]:
        UserService.get_active_user_or_404(db, user_id)
        videos = UserRepository.get_recommendations(db, user_id, limit)
        return [VideoResponse.model_validate(v) for v in videos]

    @staticmethod
    def get_yearly_views(db: Session, user_id: int, year: int | None = None) -> dict:
        UserService.get_active_user_or_404(db, user_id)
        if year is None:
            year = datetime.now().year
        total = UserRepository.get_yearly_view_count(db, user_id, year) or 0
        return {"user_id": user_id, "total_views": int(total), "year": year}

    @staticmethod
    def get_favorite_creator(
        db: Session, user_id: int, year: int | None = None
    ) -> dict:
        UserService.get_active_user_or_404(db, user_id)
        if year is None:
            year = datetime.now().year
        result = UserRepository.get_favorite_creator(db, user_id, year)
        if not result:
            return {
                "user_id": user_id,
                "year": year,
                "favorite_creator": None,
                "message": "No views found for this year",
            }
        channel_name, view_count = result
        return {
            "user_id": user_id,
            "year": year,
            "favorite_creator": channel_name,
            "videos_watched": int(view_count or 0),
        }

    @staticmethod
    def get_reactions_count(db: Session, user_id: int, year: int | None = None) -> dict:
        UserService.get_active_user_or_404(db, user_id)
        if year is None:
            year = datetime.now().year
        comments_count, reacts_count = UserRepository.get_yearly_reaction_counts(
            db, user_id, year
        )
        total = int((comments_count or 0) + (reacts_count or 0))
        return {"user_id": user_id, "year": year, "total_reactions": total}

    @staticmethod
    def get_average_view_time_percents(db: Session, user_id: int) -> dict:
        UserService.get_active_user_or_404(db, user_id)
        avg = UserRepository.get_avg_view_percentage(db, user_id)
        if avg is None:
            return {"user_id": user_id, "average_view_percents": 0.0}
        return {
            "user_id": user_id,
            "average_view_percents": round(float(avg) * 100.0, 2),
        }

    @staticmethod
    def get_credibility_score(db: Session, user_id: int) -> UserCredibilityResponse:
        UserService.get_active_user_or_404(db, user_id)
        result = UserRepository.get_credibility_data(db, user_id)
        u_id, username, total, approved = result
        total, approved = (total or 0), (approved or 0)
        score = (approved / total * 100) if total > 0 else 0
        return UserCredibilityResponse(
            user_id=u_id,
            username=username,
            total_reports=total,
            approved_reports=approved,
            credibility_score=round(score, 2),
        )
