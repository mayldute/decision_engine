import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    input: dict = Field(
        ...,
        description="Input data for the evaluation.",
        examples=[{"age": 25, "country": "US", "amount": 1500}],
    )


class EvaluationRuleResponse(BaseModel):
    evaluation_id: uuid.UUID = Field(
        ...,
        description="Evaluation ID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    rule_id: uuid.UUID = Field(
        ...,
        description="Rule ID.",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    is_matched: bool = Field(
        ..., description="Whether the rule matched the input.", examples=[True]
    )


class EvaluationResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Evaluation ID.",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    timestamp: datetime = Field(
        ..., description="Evaluation timestamp.", examples=["2026-09-21T15:30:00Z"]
    )
    input: dict = Field(
        ...,
        description="Input data used for the evaluation.",
        examples=[{"age": 25, "country": "US", "amount": 1500}],
    )
    evaluation_rules: list[EvaluationRuleResponse]

    model_config = ConfigDict(from_attributes=True)


class EvaluationListResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Evaluation ID.",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    timestamp: datetime = Field(
        ..., description="Evaluation timestamp.", examples=["2026-09-21T15:30:00Z"]
    )

    model_config = ConfigDict(from_attributes=True)


class EvaluationRuleCreate(BaseModel):
    rule_id: uuid.UUID = Field(
        ...,
        description="Rule ID.",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    is_matched: bool = Field(
        ..., description="Whether the rule matched the input.", examples=[True]
    )
