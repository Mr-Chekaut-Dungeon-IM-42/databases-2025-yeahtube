from fastapi import APIRouter, status

from app.db.session import DBDep
from app.schemas.schemas import (
    UserCredibilityResponse,
    UserDetailedResponse,
    UserUpdate,
    VideoResponse,
)
from app.services.user import UserService

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/", response_model=dict[str, list[UserDetailedResponse]])
async def get_all_users(db: DBDep):
    return {"users": UserService.get_all_users(db)}


@router.patch("/{user_id}", response_model=UserDetailedResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: DBDep):
    return UserService.update_user(db, user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(user_id: int, db: DBDep):
    UserService.soft_delete_user(db, user_id)
    return None


@router.get("/{user_id}/recommendations", response_model=dict[str, list[VideoResponse]])
async def get_recommendations(user_id: int, db: DBDep, limit: int = 20):
    return {"videos": UserService.get_recommendations(db, user_id, limit)}


@router.get("/{user_id}/views")
async def get_user_year_views(user_id: int, db: DBDep):
    return UserService.get_yearly_views(db, user_id)


@router.get("/{user_id}/favoriteCreator")
async def get_user_favorite_creator(user_id: int, db: DBDep):
    return UserService.get_favorite_creator(db, user_id)


@router.get("/{user_id}/reactions")
async def get_user_year_reactions(user_id: int, db: DBDep):
    return UserService.get_reactions_count(db, user_id)


@router.get("/{user_id}/averageViewTime")
async def get_user_avg_view_time(user_id: int, db: DBDep):
    return UserService.get_average_view_time_percents(db, user_id)


@router.get("/{user_id}/credibility", response_model=UserCredibilityResponse)
async def get_user_credibility(user_id: int, db: DBDep):
    return UserService.get_credibility_score(db, user_id)
