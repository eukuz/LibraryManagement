from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from api.routers import main, yndx_oauth, books, collections
from api import di
import logging

import uvicorn

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(db_path: str):
    try:
        await di.init_db(db_path)
        di.yndx_oauth_cfg()
        yield
    finally:
        pass


def create_app(db_path: str) -> FastAPI:
    app = FastAPI(lifespan=lambda _: lifespan(db_path))
    app.include_router(main.router, prefix="")
    app.include_router(yndx_oauth.router, prefix="/api/yndx-oauth")
    app.include_router(books.router, prefix="/api/books")
    app.include_router(collections.router, prefix="/api/collection")
    return app


if __name__ == "__main__":
    db_path = os.environ.get("DB_DSN", "api/store/db.sqlite")
    app = create_app(db_path)
    uvicorn.run(app, host="0.0.0.0", port=9000)
