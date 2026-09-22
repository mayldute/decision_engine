import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import ActionNotFoundError
from app.models import Action
from app.modules.actions.schemas import (
    ActionCreate,
    ActionDeleteResponse,
    ActionResponse,
    ActionUpdate,
)


async def get_action_or_raise(action_id: uuid.UUID, db: AsyncSession) -> Action:
    action = await db.get(Action, action_id)

    if not action:
        raise ActionNotFoundError(f"Action with id {action_id} not found.")

    return action


async def create_action_service(
    payload: ActionCreate, db: AsyncSession
) -> ActionResponse:
    action = Action(**payload.model_dump())
    
    db.add(action)
    await db.commit()
    await db.refresh(action)

    return ActionResponse.model_validate(action)


async def get_all_actions_service(
    skip: int, limit: int, db: AsyncSession
) -> list[ActionResponse]:
    result = await db.execute(
        select(Action).order_by(Action.id).offset(skip).limit(limit)
    )
    actions = result.scalars().all()

    return [ActionResponse.model_validate(action) for action in actions]


async def get_action_service(action_id: uuid.UUID, db: AsyncSession) -> ActionResponse:
    action = await get_action_or_raise(action_id, db)

    return ActionResponse.model_validate(action)


async def update_action_service(
    action_id: uuid.UUID, payload: ActionUpdate, db: AsyncSession
) -> ActionResponse:
    action = await get_action_or_raise(action_id, db)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(action, key, value)

    await db.commit()
    await db.refresh(action)

    return ActionResponse.model_validate(action)


async def delete_action_service(
    action_id: uuid.UUID, db: AsyncSession
) -> ActionDeleteResponse:
    action = await get_action_or_raise(action_id, db)

    await db.delete(action)
    await db.commit()

    return ActionDeleteResponse(
        message="Action successfully deleted.",
        action_id=action_id,
    )
