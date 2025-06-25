import secrets
import string

from app.config import Settings

settings = Settings()

def generate_random_string(length=6):
    charset = string.digits + string.ascii_lowercase
    return ''.join(secrets.choice(charset) for _ in range(length))
