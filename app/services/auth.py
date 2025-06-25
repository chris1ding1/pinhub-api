import time
import secrets

from pydantic import EmailStr

from app.config import Settings
from app.services.email_logs import EmailLogService, EmailLogStatus, EmailLogTypes
from app.services.emails import PostmarkEmailBody, postmark_email
from app.utils import generate_random_string
from boto3.dynamodb.conditions import Attr

settings = Settings()

class AuthService:
    def verify_email_html_content(self, verification_code: str) -> str:
        return f"""
        <html>
            <body>
                <p>Please use this code to verify your {settings.APP_NAME} email address:</p>
                <h2>{verification_code}</h2>
            </body>
        </html>
        """

    async def send_auth_verify_email(self, to_mail: EmailStr, subject: str = "", mailer = settings.MAIL_MAILER):
        verify_code = generate_random_string()
        html_content = self.verify_email_html_content(verify_code)
        data = PostmarkEmailBody(
            To=to_mail,
            Subject=subject,
            HtmlBody=html_content
        )
        send_resault = await postmark_email(data)

        if send_resault.ErrorCode == 0:
            status = EmailLogStatus.SUCCESS
            expires_timestamp = int(time.time()) + (5 * 60)
        else:
            expires_timestamp = None
            status = EmailLogStatus.FAILED

        await EmailLogService().store(to_mail, EmailLogTypes.VERIFY_ADDRESS, status, verify_code, expires_timestamp, mailer, send_resault.MessageID, send_resault.model_dump())

        return send_resault

    async def verify_email(self, email: EmailStr, verify_code: str):
        query_filter = (
            Attr("email_address").eq(email) &
            Attr("business_type").eq(EmailLogTypes.VERIFY_ADDRESS) &
            Attr("send_status").eq(EmailLogStatus.SUCCESS) &
            Attr("expires_timestamp").gte(int(time.time()))
        )
        email_logs = await EmailLogService().query_by_filter(query_filter)

        if not email_logs:
            return False

        email_log = max(email_logs, key=lambda x: x.get('expires_timestamp', 0))

        if secrets.compare_digest(email_log.get('verify_code'), verify_code):
            return True
        else:
            return False

def get_auth_service():
    return AuthService()
