import uuid
from collections.abc import AsyncIterator
from typing import Annotated, NamedTuple

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TokenInvalidOrExpiredError,
    TokenUserIDMissingError,
    UserNotFoundError,
)
from app.core.tokens import ALGORITHM, SECRET_KEY
from app.database.models.user import User
from app.database.session import async_session_maker

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: DatabaseSession,
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError as err:
        raise TokenInvalidOrExpiredError("Invalid or expired access token.") from err

    user_id = payload.get("sub")

    if user_id is None:
        raise TokenUserIDMissingError("User ID missing in token.")

    try:
        user_id = uuid.UUID(user_id)
    except ValueError as err:
        raise TokenInvalidOrExpiredError("Invalid user ID in token.") from err

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError("User not found.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


class CommonContext(NamedTuple):
    db: AsyncSession
    current_user: User


async def get_common_context(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CommonContext:
    return CommonContext(db=db, current_user=current_user)
