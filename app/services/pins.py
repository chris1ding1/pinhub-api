import uuid
import filetype

from botocore.exceptions import ClientError as AwsClientError
from sqlmodel import func, select

from app.config import Settings
from app.deps import SessionDep
from app.models.user import User
from app.models.pin import Pin, PinsPublic, PinFormCreate
from app.services.aws import get_aws_service

settings = Settings()

class PinsService:
    def __init__(self, session: SessionDep):
        self.session = session

    def store(self, pinFormCreate: PinFormCreate, user: User) -> Pin:
        db_pin = Pin.model_validate(pinFormCreate, update={"user_id": user.id})
        self.session.add(db_pin)
        self.session.commit()
        return db_pin

    def index_by_user_id(self, user: User):
        count_statement = (
            select(func.count())
        .select_from(Pin)
            .where(Pin.user_id == user.id)
        )
        count = self.session.exec(count_statement).one()
        statement = (
            select(Pin)
            .where(Pin.user_id == user.id)
        )
        pins = self.session.exec(statement).all()
        return PinsPublic(data=pins, count=count)

    @staticmethod
    def uplpad_file(file_content: bytes, user: User):
        file_name = str(uuid.uuid4())
        first_two = file_name[:2]
        third_fourth = file_name[2:4]

        file_kind = filetype.guess(file_content)
        if file_kind is None:
            file_ext = 'bin'
        else:
            file_ext = file_kind.extension

        file_path = f"pins/{user.id}/{first_two}/{third_fourth}/{file_name}.{file_ext}"
        bucket_name = settings.ASSET_STORAGE_BUCKET_NAME

        print(f"file_path={file_path}, bucket_name={bucket_name}")

        aws_service = get_aws_service()
        s3_client = aws_service.get_s3()
        try:
            s3_client.Object(bucket_name, file_path).put(
                Body=file_content,
                ContentType=file_kind.mime if file_kind else 'application/octet-stream'
            )
        except AwsClientError as e:
            raise False

        return  f"/{file_path}"
