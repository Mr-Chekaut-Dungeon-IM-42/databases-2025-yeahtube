from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from . import routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup

    yield

    # Shutdown


app = FastAPI(lifespan=lifespan)
for router in routers.__all__:
    app.include_router(getattr(routers, router))
