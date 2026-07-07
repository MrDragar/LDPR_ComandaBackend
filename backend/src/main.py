import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.application.routes import root_router
from src.core import config
from src.core.containers import Container

logging.basicConfig(
    level=config.log_level,
    format=config.log_format,
    filename=config.log_file,
    filemode="a"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()
    await container.database().create_database()
    yield


app = FastAPI(title="LDPR MiniApp API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Если detail это словарь с error и message, возвращаем его как есть
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    # Иначе стандартный формат
    return JSONResponse(status_code=exc.status_code,
                        content={"error": "UNKNOWN", "message": str(exc.detail)})


app.include_router(root_router)
