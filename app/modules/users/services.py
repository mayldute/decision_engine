import uuid
from datetime import UTC, datetime

from jose import JWTError, jwt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TokenInvalidOrExpiredError,
    TokenInvalidTypeError,
    UserAlreadyRegisteredError,
    UserNotFoundError,
    UserWrongPasswordError,
)
from app.core.security import hash_password, verify_password, verify_token
from app.core.tokens import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_tokens_for_user,
)
from app.database.models.token import RefreshToken
from app.database.models.user import User
from app.modules.users.schemas import Token, UserCreate, UserLogin, UserResponse


async def register_user_service(payload: UserCreate, db: AsyncSession) -> UserResponse:
    result = await db.execute(
        select(User).where(
            (User.email == payload.email) | (User.nickname == payload.nickname)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise UserAlreadyRegisteredError("User has already registered.")

    user = User(
        nickname=payload.nickname,
        email=payload.email,
        hashed_password=hash_password(payload.password1),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


async def authenticate_user_service(payload: UserLogin, db: AsyncSession) -> Token:
    if payload.nickname:
        result = await db.execute(select(User).where(User.nickname == payload.nickname))
    else:
        result = await db.execute(select(User).where(User.email == payload.email))

    user = result.scalar_one_or_none()

    if not user:
        raise UserNotFoundError(
            f"User with nickname {payload.nickname}/ email {payload.email} not found."
        )

    if not verify_password(payload.password, user.hashed_password):
        raise UserWrongPasswordError("Wrong password.")

    return await get_tokens_for_user(user, db)


async def logout_user_service(current_user: User, db: AsyncSession) -> dict:
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == current_user.id)
    )

    await db.commit()

    return {"message": "Logout successful"}


async def refresh_user_token_service(refresh_token: str, db: AsyncSession) -> dict:
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError as err:
        raise TokenInvalidOrExpiredError("Invalid or expired refresh token.") from err

    if payload.get("type") != "refresh":
        raise TokenInvalidTypeError("Invalid token type.")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError, TypeError) as err:
        raise TokenInvalidOrExpiredError("Invalid user ID in refresh token.") from err

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise TokenInvalidOrExpiredError("Refresh token expired or not found.")

    if not verify_token(refresh_token, stored_token.hashed_token):
        raise TokenInvalidOrExpiredError("Refresh token expired or not found.")

    if stored_token.expires_at < datetime.now(UTC):
        raise TokenInvalidOrExpiredError("Refresh token expired.")

    user = await db.get(User, user_id)

    if not user:
        raise UserNotFoundError("User not found.")

    user_data = {
        "sub": str(user.id),
        "email": user.email,
    }

    return {"access_token": create_access_token(user_data)}


async def get_user_service(current_user: User) -> UserResponse:
    return UserResponse.model_validate(current_user)
