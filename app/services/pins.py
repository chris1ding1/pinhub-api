import uuid
import filetype
import httpx
from uuid import UUID

from botocore.exceptions import ClientError as AwsClientError
from sqlmodel import func, select, delete

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

    def get_by_id_and_user(self, pin_id: uuid.UUID, user_id: uuid.UUID) -> Pin | None:
        statement = select(Pin).where(
            Pin.id == pin_id,
            Pin.user_id == user_id,
            Pin.deleted_at.is_(None)
        )
        return self.session.exec(statement).first()

    def delete_by_id(self, id: UUID) -> None:
        statement = delete(Pin).where(Pin.id == id)
        self.session.exec(statement)
        self.session.commit()

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

        file_name = f"{file_name}.{file_ext}"
        file_path = f"pins/{user.id}/{first_two}/{third_fourth}/{file_name}"
        bucket_name = settings.ASSET_STORAGE_BUCKET_NAME

        print(f"file_path={file_path}, bucket_name={bucket_name}")

        aws_service = get_aws_service()
        s3_client = aws_service.get_s3()
        text_content = ""
        try:
            s3_client.Object(bucket_name, file_path).put(
                Body=file_content,
                ContentType=file_kind.mime if file_kind else 'application/octet-stream'
            )
            if file_ext == "webm":
                transcribe_client = aws_service.get_transcribe()
                response = transcribe_client.start_transcription_job(
                    TranscriptionJobName=f"transcribe-{file_name}",
                    Media={'MediaFileUri': f"s3://{bucket_name}/{file_path}"},
                    MediaFormat='webm',
                    IdentifyLanguage=True,
                )
                job_name = response['TranscriptionJob']['TranscriptionJobName']
                while True:
                    transcribe_job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                    job_status = transcribe_job['TranscriptionJob']['TranscriptionJobStatus']

                    if job_status == 'COMPLETED':
                        transcript_file_uri = transcribe_job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        with httpx.Client() as httpClient:
                            transcript_response = httpClient.get(transcript_file_uri)
                            transcript_data = transcript_response.json()
                            text_content = transcript_data['results']['transcripts'][0]['transcript']
                        break
                    elif job_status == 'FAILED':
                        print(f"Transcription failed: {transcribe_job['TranscriptionJob'].get('FailureReason', 'Unknown error')}")
                        text_content = ""
                        break

                    import time
                    time.sleep(1)
        except AwsClientError as e:
            print(f"AwsClientError: {e}")
            raise e

        return  {
            "name": file_name,
            "text": text_content,
            "path": file_path,
        }
