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
    id: uuid.UUID = Field(..., description="Action ID.")
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
