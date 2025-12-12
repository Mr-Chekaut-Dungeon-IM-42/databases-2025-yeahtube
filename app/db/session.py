from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DB_URL = os.environ.get("DB_URL", "postgresql://admin:password@postgres:5432/db_labs")

engine = create_engine(DB_URL, future=True)

SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, future=True)


def get_session() -> Session:
    return SessionLocal()


DBDep = Annotated[Session, Depends(get_session)]
