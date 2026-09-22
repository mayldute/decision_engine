import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import LogicalOperator
from app.modules.actions.schemas import ActionCreate, ActionResponse
from app.modules.conditions.schemas import ConditionCreate, ConditionResponse


class RuleCreate(BaseModel):
    name: str = Field(
        ...,
        description="Name of the rule.",
        examples=["1st rule"],
    )
    description: str | None = Field(
        default=None,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        default=None,
        description="Logical operator of the rule.",
        examples=["AND"],
    )
    priority: int = Field(
        ...,
        description="Priority of the rule (priority >= 1 AND priority <= 100).",
        examples=[99],
    )
    is_active: bool = Field(
        ...,
        description="Whether the rule is currently active.",
        examples=[True],
    )

    condition_ids: list[uuid.UUID] | None = None
    new_conditions: list[ConditionCreate] | None = None

    action_id: uuid.UUID | None = None
    new_action: ActionCreate | None = None

    @model_validator(mode="before")
    def validate_rule(cls, values):
        logical_operator = values.get("logical_operator")
        condition_ids = values.get("condition_ids")
        new_conditions = values.get("new_conditions")
        action_id = values.get("action_id")
        new_action = values.get("new_action")

        if condition_ids is not None and new_conditions is not None:
            raise ValueError(
                "Provide either condition_ids or new_conditions, not both."
            )

        if condition_ids is None and new_conditions is None:
            raise ValueError("Either condition_ids or new_conditions must be provided.")

        if condition_ids is not None and not condition_ids:
            raise ValueError("At least one condition must be provided.")

        if new_conditions is not None and not new_conditions:
            raise ValueError("At least one condition must be provided.")

        if action_id is not None and new_action is not None:
            raise ValueError("Provide either action_id or new_action, not both.")

        if action_id is None and new_action is None:
            raise ValueError("Either action_id or new_action must be provided.")

        conditions = condition_ids if condition_ids is not None else new_conditions

        if len(conditions) > 1 and logical_operator is None:
            raise ValueError(
                "Logical operator cannot be None if there is more than one condition."
            )

        return values


class RuleResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Rule ID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="Name of the rule.",
        examples=["1st rule"],
    )
    description: str | None = Field(
        ...,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        ...,
        description="Logical operator of the rule.",
        examples=["AND"],
    )
    priority: int = Field(
        ...,
        description="Priority of the rule (priority >= 1 AND priority <= 100).",
        examples=[99],
    )
    is_active: bool = Field(
        ...,
        description="Whether the rule is currently active.",
        examples=[True],
    )

    conditions: list[ConditionResponse]
    action: ActionResponse

    model_config = ConfigDict(from_attributes=True)


class RuleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        description="Name of the rule.",
        examples=["1st rule"],
    )
    description: str | None = Field(
        default=None,
        description="Description of the rule.",
        examples=["Description of the 1st rule."],
    )
    logical_operator: LogicalOperator | None = Field(
        default=None,
        description="Logical operator of the rule.",
        examples=["AND"],
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

    condition_ids: list[uuid.UUID] | None = None
    new_conditions: list[ConditionCreate] | None = None

    action_id: uuid.UUID | None = None
    new_action: ActionCreate | None = None

    @model_validator(mode="before")
    def validate_rule(cls, values):
        condition_ids = values.get("condition_ids")
        new_conditions = values.get("new_conditions")
        action_id = values.get("action_id")
        new_action = values.get("new_action")

        if condition_ids is not None and new_conditions is not None:
            raise ValueError(
                "Provide either condition_ids or new_conditions, not both."
            )

        if action_id is not None and new_action is not None:
            raise ValueError("Provide either action_id or new_action, not both.")

        return values


class RuleDeleteResponse(BaseModel):
    message: str = Field(
        ...,
        description="Confirmation message indicating that the rule was deleted.",
        examples=["Rule deleted successfully."],
    )
    rule_id: uuid.UUID = Field(
        ...,
        description="ID of the deleted rule.",
        examples=["550e8400-e29b-41d4-a716-446655412345"],
    )
