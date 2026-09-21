import uuid

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class ActionCreate(BaseModel):
    field: str = Field(..., description="Name of the field.", examples=["weather"])
    value: JsonValue = Field(
        ...,
        description="Value to assign.",  # TO DO: change description after adding type
        examples=["warm"],
    )


class ActionResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Action ID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    field: str = Field(..., description="Name of the field.", examples=["weather"])
    value: JsonValue = Field(
        ...,
        description="Value to assign.",  # TO DO: change description after adding type
        examples=["warm"],
    )

    model_config = ConfigDict(from_attributes=True)


class ActionUpdate(BaseModel):
    field: str | None = Field(
        default=None, description="Name of the field.", examples=["weather"]
    )
    value: JsonValue | None = Field(
        default=None,
        description="Value to assign.",  # TO DO: change description after adding type
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
