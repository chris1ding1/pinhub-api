from fastapi import FastAPI

from app.routers import pins

app = FastAPI()
app.include_router(pins.router)
