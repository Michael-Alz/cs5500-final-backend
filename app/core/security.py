from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return str(bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8"))


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bool(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")))


def create_access_token(subject: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)
    to_encode = {"sub": subject, "exp": expire}
    return str(jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256"))


def verify_token(token: str) -> str | None:
    """Verify and decode a JWT token, return the subject."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        subject = payload.get("sub")
        return str(subject) if subject is not None else None
    except JWTError:
        return None
