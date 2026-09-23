import uuid
from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_token
from app.database.models import RefreshToken, User

SECRET_KEY = settings.jwt.jwt_secret_key
ALGORITHM = settings.jwt.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt.jwt_refresh_token_expire_days


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_tokens_for_user(user: User, db: AsyncSession) -> dict:
    user_data = {
        "sub": str(user.id),
        "email": user.email,
    }

    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    if user.refresh_token:
        user.refresh_token.hashed_token = hash_token(refresh_token)
        user.refresh_token.expires_at = datetime.now(UTC) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    else:
        user.refresh_token = RefreshToken(
            hashed_token=hash_token(refresh_token),
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            created_at=datetime.now(UTC),
        )

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def create_activation_token(user_id: uuid.UUID) -> str:
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    payload = {
        "sub": str(user_id),
        "type": "activation",
        "exp": datetime.now(UTC) + timedelta(hours=24),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_email_change_token(user_id: uuid.UUID, new_email: str) -> str:
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")
    if not new_email:
        raise ValueError("New email cannot be empty")

    payload = {
        "sub": str(user_id),
        "new_email": new_email,
        "type": "email_change",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
