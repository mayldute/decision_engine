import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConditionNotFoundError
from app.database.models import Condition
from app.modules.conditions.schemas import (
    ConditionCreate,
    ConditionDeleteResponse,
    ConditionResponse,
    ConditionUpdate,
)


async def get_condition_or_raise(
    condition_id: uuid.UUID, db: AsyncSession
) -> Condition:
    condition = await db.get(Condition, condition_id)

    if not condition:
        raise ConditionNotFoundError(f"Condition with id {condition_id} not found.")

    return condition


async def create_condition_service(
    payload: ConditionCreate, db: AsyncSession
) -> ConditionResponse:
    condition = Condition(**payload.model_dump())
    db.add(condition)
    await db.commit()
    await db.refresh(condition)

    return ConditionResponse.model_validate(condition)


async def get_all_conditions_service(
    skip: int, limit: int, db: AsyncSession
) -> list[ConditionResponse]:
    result = await db.execute(
        select(Condition).order_by(Condition.id).offset(skip).limit(limit)
    )
    conditions = result.scalars().all()

    return [ConditionResponse.model_validate(condition) for condition in conditions]


async def get_condition_service(
    condition_id: uuid.UUID, db: AsyncSession
) -> ConditionResponse:
    condition = await get_condition_or_raise(condition_id, db)

    return ConditionResponse.model_validate(condition)


async def update_condition_service(
    condition_id: uuid.UUID, payload: ConditionUpdate, db: AsyncSession
) -> ConditionResponse:
    condition = await get_condition_or_raise(condition_id, db)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(condition, key, value)

    await db.commit()
    await db.refresh(condition)

    return ConditionResponse.model_validate(condition)


async def delete_condition_service(
    condition_id: uuid.UUID, db: AsyncSession
) -> ConditionDeleteResponse:
    condition = await get_condition_or_raise(condition_id, db)

    await db.delete(condition)
    await db.commit()

    return ConditionDeleteResponse(
        message="Condition successfully deleted.",
        condition_id=condition_id,
    )
