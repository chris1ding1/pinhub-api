import secrets
import string
from pathlib import Path

from app.config import Settings

settings = Settings()

def generate_random_string(length=6):
    charset = string.digits + string.ascii_lowercase
    return ''.join(secrets.choice(charset) for _ in range(length))

def get_path_segment(path: str, index: int) -> str | None:
    if not path:
        return None

    path_obj = Path(path)
    parts = path_obj.parts
    if len(parts) > index:
        return parts[index]
    return None
