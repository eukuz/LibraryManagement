from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

    @app.exception_handler(HTTPException)
    async def _(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": "Server Error"}
        )

    @app.exception_handler(ValueError)
    async def _(request, exc):
        logging.exception(exc)
        return JSONResponse(
            status_code=500,
            content={"message": "Server Error"}
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
    uvicorn.run(app, host=host, port=port)
