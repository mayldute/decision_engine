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
            selectinload(Evaluation.evaluation_rules).selectinload(EvaluationRule.rule)
        )
        .where(
            Evaluation.id == evaluation_id,
            Evaluation.user_id == current_user.id,
        )
    )

    evaluation = result.scalar_one_or_none()

    if evaluation is None:
        raise EvaluationNotFoundError(f"Evaluation with id {evaluation_id} not found.")

    return EvaluationResponse.model_validate(evaluation)
