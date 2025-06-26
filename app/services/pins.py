from app.deps import SessionDep
from app.models.user import User
from app.models.pin import PinFormCreate, Pin

class PinsService:
    def __init__(self, session: SessionDep):
        self.session = session

    def store(self, pinFormCreate: PinFormCreate, user: User) -> Pin:
        db_pin = Pin.model_validate(pinFormCreate, update={"user_id": user.id})
        self.session.add(db_pin)
        self.session.commit()
        return db_pin
