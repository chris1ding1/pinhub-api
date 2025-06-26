from fastapi import APIRouter

from app.models.common import IndexResource
from app.deps import CurrentUser, SessionDep
from app.services.pins import PinsService


router = APIRouter()

@router.get("/users/pins")
async def users_pins(user: CurrentUser, session: SessionDep, response_model=IndexResource):
    pins_service = PinsService(session)
    pins = pins_service.index_by_user_id(user)
    return IndexResource(
        data={
            "total": pins.count,
            "items": pins.data,
        }
    )
