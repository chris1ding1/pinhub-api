from fastapi import APIRouter

router = APIRouter()


@router.post("/links")
async def store(link):
    return ""


@router.put("/links/{link_uid}")
async def update(link_uid: int):
    return ""


@router.delete("/links/{link_uid}")
def destroy(link_uid: int):
    return ""
