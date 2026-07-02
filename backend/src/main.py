from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.application.routes import root_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(root_router)
