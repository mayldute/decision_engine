import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import LogicalOperator
from app.modules.actions.schemas import ActionCreate, ActionResponse, ActionUpdate
from app.modules.conditions.schemas import (
    ConditionCreate,
    ConditionResponse,
    ConditionUpdate,
)


class RuleCreate(BaseModel):
    name: str = Field(..., description="Name of the rule.", examples=["1st rule"])
    description: str | None = Field(
        default=None,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        default=None, description="Logical operators of the rule.", examples=["AND"]
    )
    priority: int = Field(
        ...,
        description="Priority of the rule (priority >= 1 AND priority <= 100).",
        examples=[99],
    )
    is_active: bool = Field(
        ..., description="Whether the rule is currently active.", examples=[True]
    )

    conditions: list[ConditionCreate]
    action: ActionCreate

    @model_validator(mode="before")
    def validate_rule(cls, values):
        logical_operator = values.get("logical_operator")
        conditions = values.get("conditions")

        if len(conditions) > 1 and logical_operator is None:
            raise ValueError(
                "Logical operator can not be None if there is more than one condition."
            )

        return values


class RuleResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Rule ID.")
    name: str = Field(..., description="Name of the rule.", examples=["1st rule"])
    description: str | None = Field(
        ...,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        ..., description="Logical operators of the rule.", examples=["AND"]
    )
    priority: int = Field(
        ...,
        description="Priority of the rule (priority >= 1 AND priority <= 100).",
        examples=[99],
    )
    is_active: bool = Field(
        ..., description="Whether the rule is currently active.", examples=[True]
    )

    conditions: list[ConditionResponse]
    action: ActionResponse

    model_config = ConfigDict(from_attributes=True)


class RuleUpdate(BaseModel):
    name: str | None = Field(
        default=None, description="Name of the rule.", examples=["1st rule"]
    )
    description: str | None = Field(
        default=None,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        default=None, description="Logical operators of the rule.", examples=["AND"]
    )
    priority: int | None = Field(
        default=None,
        description="Priority of the rule (priority >= 1 AND priority <= 100).",
        examples=[99],
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the rule is currently active.",
        examples=[True],
    )

    conditions: list[ConditionUpdate] | None = None
    action: ActionUpdate | None = None

    @model_validator(mode="before")
    def validate_rule(cls, values):
        logical_operator = values.get("logical_operator")
        conditions = values.get("conditions")

        if conditions and len(conditions) > 1 and logical_operator is None:
            raise ValueError(
                "Logical operator can not be None if there is more than one condition."
            )

        return values
