from fastapi import APIRouter

router = APIRouter()


@router.post("/pins")
async def store(link):
    return ""


@router.put("/pins/{pin_uid}")
async def update(pin_uid: int):
    return ""


@router.delete("/pins/{pin_uid}")
def destroy(pin_uid: int):
    return ""
