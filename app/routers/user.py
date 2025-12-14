from fastapi import APIRouter
from sqlalchemy import select

from app.db.models import User
from app.db.session import DBDep

router = APIRouter(prefix="/user")


@router.get("/test")
async def test(db: DBDep):
    # user = User(
    #     id=1, username="Test", email="test@example.org", created_at="2025-07-07"
    # )
    # db.add(user)
    # db.commit()

    users = db.execute(select(User)).scalars().all()
    return {"users": [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at} for u in users]}