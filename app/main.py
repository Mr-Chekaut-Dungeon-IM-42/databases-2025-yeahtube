from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .presentation import routers
from .presentation.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup

    yield

    # Shutdown


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
for router in routers.__all__:
    app.include_router(getattr(routers, router))
