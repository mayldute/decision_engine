import uuid

from pydantic import BaseModel, ConfigDict, Field, JsonValue

from app.models.enums import ComparisonOperator


class ConditionCreate(BaseModel):
    field: str = Field(..., description="Name of the field.", examples=["temperature"])
    operator: ComparisonOperator = Field(
        ..., description="Comparison operator.", examples=["=="]
    )
    value: JsonValue = Field(
        ...,
        description="Value to compare against (primitive, list, or dict).",
        examples=[25.5],
    )


class ConditionResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Condition ID.")
    field: str = Field(..., description="Name of the field.", examples=["temperature"])
    operator: ComparisonOperator = Field(
        ..., description="Comparison operator.", examples=["="]
    )
    value: JsonValue = Field(
        ...,
        description="Value to compare against (primitive, list, or dict).",
        examples=[25.5],
    )

    model_config = ConfigDict(from_attributes=True)


class ConditionUpdate(BaseModel):
    field: str | None = Field(
        default=None, description="Name of the field.", examples=["temperature"]
    )
    operator: ComparisonOperator | None = Field(
        default=None, description="Comparison operator.", examples=["="]
    )
    value: JsonValue | None = Field(
        default=None,
        description="Value to compare against (primitive, list, or dict).",
        examples=[25.5],
    )
