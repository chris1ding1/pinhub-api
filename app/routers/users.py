from fastapi import APIRouter

from app.deps import CurrentUser

router = APIRouter()

@router.get("/users/pins")
async def pins_index(user: CurrentUser):
    pass
