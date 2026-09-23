import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import ActionNotFoundError
from app.database.dependencies import CommonContext, get_common_context
from app.modules.actions.schemas import (
    ActionCreate,
    ActionDeleteResponse,
    ActionResponse,
    ActionUpdate,
)
from app.modules.actions.services import (
    create_action_service,
    delete_action_service,
    get_action_service,
    get_all_actions_service,
    update_action_service,
)

router = APIRouter(prefix="/actions", tags=["[actions] actions"])


@router.post(
    "/",
    response_model=ActionResponse,
    summary="Create action.",
    status_code=201,
)
async def create_action(
    payload: ActionCreate, context: CommonContext = Depends(get_common_context)
):
    return await create_action_service(payload, context.current_user, context.db)


@router.get(
    "/",
    response_model=list[ActionResponse],
    summary="Get all actions",
    status_code=200,
)
async def get_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    context: CommonContext = Depends(get_common_context),
):
    return await get_all_actions_service(skip, limit, context.current_user, context.db)


@router.get(
    "/{action_id}",
    response_model=ActionResponse,
    summary="Get action by ID.",
    status_code=200,
)
async def get_action_by_id(
    action_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await get_action_service(action_id, context.current_user, context.db)
    except ActionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Action not found.") from err


@router.patch(
    "/{action_id}",
    response_model=ActionResponse,
    summary="Update action by ID.",
    status_code=200,
)
async def update_action(
    action_id: uuid.UUID,
    payload: ActionUpdate,
    context: CommonContext = Depends(get_common_context),
):
    try:
        return await update_action_service(
            action_id, payload, context.current_user, context.db
        )
    except ActionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Action not found.") from err


@router.delete(
    "/{action_id}",
    response_model=ActionDeleteResponse,
    summary="Delete action by ID.",
    status_code=200,
)
async def delete_action(
    action_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await delete_action_service(action_id, context.current_user, context.db)
    except ActionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Action not found.") from err
