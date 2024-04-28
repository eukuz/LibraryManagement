from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(main.router, prefix="")
    app.include_router(yndx_oauth.router, prefix="/api/yndx-oauth")
    app.include_router(books.router, prefix="/api/books")
    app.include_router(collections.router, prefix="/api/collection")
    return app


if __name__ == "__main__":
    db_path = os.environ.get("DB_DSN", "api/store/db.sqlite")
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", '9000'))
    app = create_app(db_path)
<<<<<<< HEAD
    uvicorn.run(app, host="127.0.0.1", port=9000)
=======
    uvicorn.run(app, host=host, port=port)
>>>>>>> 87ceaf305346a676b05233a6317aaaaa6d4279dd
