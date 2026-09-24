import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EvaluationNotFoundError
from app.database.models.evaluation import Evaluation
from app.database.models.evaluation_rule import EvaluationRule
from app.database.models.user import User
from app.modules.evaluations.schemas import (
    EvaluationCreate,
    EvaluationListResponse,
    EvaluationResponse,
    EvaluationRuleCreate,
    EvaluationRuleResponse,
)


async def create_evaluation_service(
    payload: EvaluationCreate,
    evaluation_results: list[EvaluationRuleCreate],
    current_user: User,
    db: AsyncSession,
) -> EvaluationResponse:

    evaluation = Evaluation(
        input=payload.input,
        user_id=current_user.id,
    )

    db.add(evaluation)

    for result in evaluation_results:
        evaluation_rule = EvaluationRule(
            evaluation=evaluation,
            rule_id=result.rule_id,
            is_matched=result.is_matched,
            resulting_input=result.resulting_input,
        )
        db.add(evaluation_rule)

    await db.commit()

    result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.evaluation_rules))
        .where(Evaluation.id == evaluation.id)
    )

    evaluation = result.scalar_one()

    return EvaluationResponse.model_validate(evaluation)



async def get_all_evaluations_service(
    skip: int, limit: int, current_user: User, db: AsyncSession
) -> list[EvaluationListResponse]:
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.user_id == current_user.id)
        .order_by(Evaluation.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    evaluations = result.scalars().all()

    return [
        EvaluationListResponse.model_validate(evaluation) for evaluation in evaluations
    ]


async def get_evaluation_service(
    evaluation_id: uuid.UUID, current_user: User, db: AsyncSession
) -> EvaluationResponse:
    result = await db.execute(
        select(Evaluation)
        .options(
            selectinload(Evaluation.evaluation_rules)
        )
        .where(
            Evaluation.id == evaluation_id,
            Evaluation.user_id == current_user.id,
        )
    )

    evaluation = result.scalar_one_or_none()

    if evaluation is None:
        raise EvaluationNotFoundError(
            f"Evaluation with id {evaluation_id} not found."
        )

    return EvaluationResponse(
        id=evaluation.id,
        timestamp=evaluation.timestamp,
        input=evaluation.input,
        evaluation_rules=[
            EvaluationRuleResponse(
                evaluation_id=evaluation_rule.evaluation_id,
                rule_id=evaluation_rule.rule_id,
                is_matched=evaluation_rule.is_matched,
                resulting_input=evaluation_rule.resulting_input,
            )
            for evaluation_rule in evaluation.evaluation_rules
        ],
    )