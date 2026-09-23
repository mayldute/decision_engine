import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    nickname: str = Field(..., description="User's nickname.", examples=["user123"])
    email: EmailStr = Field(
        ..., description="User's email.", examples=["user123@example.com"]
    )
    password1: str = Field(
        ..., 
        min_length=8, 
        description="User's password.", 
        examples=["StrongPass123!"],
    )
    password2: str = Field(
        ...,
        min_length=8,
        description="Password confirmation.",
        examples=["StrongPass123!"],
    )

    @model_validator(mode="after")
    def check_passwords(self):
        if not any(c.islower() for c in self.password1):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not any(c.isupper() for c in self.password1):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not any(c.isdigit() for c in self.password1):
            raise ValueError("Password must contain at least one digit.")

        if self.password1 != self.password2:
            raise ValueError("Passwords do not match.")

        return self


class UserLogin(BaseModel):
    nickname: str | None = Field(
        default=None, description="User's nickname.", examples=["user123"]
    )
    email: EmailStr | None = Field(
        default=None, description="User's email.", examples=["user123@example.com"]
    )
    password: str = Field(
        ..., description="Password confirmation.", examples=["StrongPass123!"]
    )

    @model_validator(mode="after")
    def nickname_or_email(self):
        if self.nickname is None and self.email is None:
            raise ValueError("Either nickname or email must be provided.")

        if self.nickname is not None and self.email is not None:
            raise ValueError("Provide either nickname or email, not both.")

        return self


class UserResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="User's ID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    nickname: str = Field(..., description="User's nickname.", examples=["user123"])
    email: EmailStr = Field(
        ..., description="User's email.", examples=["user123@example.com"]
    )

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str = Field(
        ..., description="JWT access token", examples=["eyJhbGciOiJIUzI1..."]
    )
    refresh_token: str = Field(
        ..., description="JWT refresh token", examples=["eyJhbGciOiJIUzI1..."]
    )
    token_type: str = Field(..., description="Token type", example="bearer")
