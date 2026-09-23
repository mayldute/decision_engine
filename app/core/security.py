from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        raise ValueError("Password or hashed password cannot be empty.")

    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    if not token:
        raise ValueError("Token can not be empty.")

    return pwd_context.hash(token)


def verify_token(plain_token: str, hashed_token: str) -> bool:
    if not plain_token or not hash_password:
        raise ValueError("Token or hashed password cannot be empty.")

    return pwd_context.verify(plain_token, hashed_token)
