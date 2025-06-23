"""main"""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.routers import auth

app = FastAPI()


@lru_cache
def get_settings():
    """Creating the Settings only once"""
    return Settings()

# Set all CORS enabled origins
if get_settings().all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
#app.include_router(pins.router)
#app.include_router(users.router)
app.include_router(auth.router)
