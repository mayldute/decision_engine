import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    nickname: str = Field(..., description="User's nickname.", examples=["user123"])
    email: EmailStr = Field(
        ..., description="User's email.", examples=["user123@example.com"]
    )


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
