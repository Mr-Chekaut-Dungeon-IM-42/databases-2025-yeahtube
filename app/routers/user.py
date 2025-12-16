from fastapi import APIRouter
from sqlalchemy import select

from app.db.models import User
from app.db.session import DBDep

router = APIRouter(prefix="/user")


@router.get("/test")
async def test(db: DBDep):
    users = db.execute(select(User)).scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at,
            }
            for u in users
        ]
    }

