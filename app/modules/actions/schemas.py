import uuid

from pydantic import BaseModel, ConfigDict, Field, JsonValue

from app.database.models.enums import ActionType


class ActionCreate(BaseModel):
    field: str = Field(..., description="Name of the field.", examples=["weather"])
    type: ActionType = Field(
        ..., description="Type of acftion.", examples=["SET_VALUE"]
    )
    value: JsonValue = Field(
        ...,
        description="Value.",
        examples=["warm"],
    )


class ActionResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Action ID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    field: str = Field(..., description="Name of the field.", examples=["weather"])
    type: ActionType = Field(
        ..., description="Type of acftion.", examples=["SET_VALUE"]
    )
    value: JsonValue = Field(
        ...,
        description="Value.",
        examples=["warm"],
    )

    model_config = ConfigDict(from_attributes=True)


class ActionUpdate(BaseModel):
    field: str | None = Field(
        default=None, description="Name of the field.", examples=["weather"]
    )
    type: ActionType | None = Field(
        default=None,
        description="Type of acftion.",
        examples=["SET_VALUE"],
    )
    value: JsonValue | None = Field(
        default=None,
        description="Value.",
        examples=["warm"],
    )


class ActionDeleteResponse(BaseModel):
    message: str = Field(
        ...,
        description="Confirmation message indicating that the action was deleted.",
        examples=["Action deleted successfully."],
    )
    action_id: uuid.UUID = Field(
        ...,
        description="ID of the deleted action.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
