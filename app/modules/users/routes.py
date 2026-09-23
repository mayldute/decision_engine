from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TokenInvalidOrExpiredError,
    TokenInvalidTypeError,
    UserAlreadyRegisteredError,
    UserNotFoundError,
    UserWrongPasswordError,
)
from app.database.dependencies import (
    CommonContext,
    bearer_scheme,
    get_common_context,
    get_db,
)
from app.modules.users.schemas import Token, UserCreate, UserLogin, UserResponse
from app.modules.users.services import (
    authenticate_user_service,
    get_user_service,
    logout_user_service,
    refresh_user_token_service,
    register_user_service,
)

router = APIRouter(prefix="/users", tags=["[users] users"])


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register user.",
    status_code=201,
)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await register_user_service(payload, db)
    except UserAlreadyRegisteredError as err:
        raise HTTPException(
            status_code=409, detail="User has already registered."
        ) from err


@router.post(
    "/login",
    response_model=Token,
    summary="Login user.",
    status_code=200,
)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        return await authenticate_user_service(payload, db)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail="User not found.") from err
    except UserWrongPasswordError as err:
        raise HTTPException(
            status_code=401,
            detail="Wrong password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@router.post(
    "/logout",
    summary="Logout user.",
    status_code=200,
)
async def logout_user(context: CommonContext = Depends(get_common_context)) -> dict:
    return await logout_user_service(context.current_user, context.db)


@router.post(
    "/refresh", summary="Get new access token using refresh token", status_code=200
)
async def refresh_user_token(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await refresh_user_token_service(token.credentials, db)
    except TokenInvalidOrExpiredError as err:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found/invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except TokenInvalidTypeError as err:
        raise HTTPException(
            status_code=401,
            detail="Invalid token type.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@router.get(
    "/",
    response_model=UserResponse,
    summary="Get user.",
    status_code=200,
)
async def get_user(context: CommonContext = Depends(get_common_context)):
    return await get_user_service(context.current_user)
