from fastapi import APIRouter
from sqlalchemy import select

from app.db.models import User
from app.db.session import DBDep

router = APIRouter(prefix="/user")


@router.get("/test")
async def test(db: DBDep):
    users = list(db.execute(select(User).where(User.id == 1)).scalars().all())
    user = db.execute(select(User).where(User.created_at.is_not(None))).scalar()

    user2 = User(
        id=1, username="Test", email="test@example.org", created_at="2025-07-07"
    )
    db.add(user2)
    db.commit()
