import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _validate_jwt_secret():
    """Validate that JWT_SECRET has been changed from the default in production."""
    weak_secrets = [
        "dev-secret-change-in-production",
        "change-me-to-a-random-64-char-hex-string",
        "your-secret-key",
    ]
    if settings.JWT_SECRET in weak_secrets or len(settings.JWT_SECRET) < 32:
        if settings.DEBUG:
            logger.warning(
                "⚠ JWT_SECRET 使用弱密钥！生产环境请设置至少32字符的随机密钥。"
                "  python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        else:
            logger.critical(
                "⛔ 生产环境 JWT_SECRET 不安全！请立即设置随机密钥后重启服务。"
            )


_validate_jwt_secret()


def hash_password(password: str) -> str:
    salt = settings.JWT_SECRET.encode()[:32]
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000).hex()


def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(plain), hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


async def get_current_user(token: str | None = Depends(oauth2_scheme)):
    if token is None:
        return None
    payload = decode_token(token)
    if payload is None:
        return None
    return payload
