from fastapi import APIRouter

router = APIRouter()

@router.get("/users/pins")
async def pins_index():
    pass
