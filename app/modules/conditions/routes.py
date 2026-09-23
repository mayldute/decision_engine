import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import ConditionNotFoundError
from app.database.dependencies import CommonContext, get_common_context
from app.modules.conditions.schemas import (
    ConditionCreate,
    ConditionDeleteResponse,
    ConditionResponse,
    ConditionUpdate,
)
from app.modules.conditions.services import (
    create_condition_service,
    delete_condition_service,
    get_all_conditions_service,
    get_condition_service,
    update_condition_service,
)

router = APIRouter(prefix="/conditions", tags=["[conditions] conditions"])


@router.post(
    "/", response_model=ConditionResponse, summary="Create condition.", status_code=201
)
async def create_condition(
    payload: ConditionCreate, context: CommonContext = Depends(get_common_context)
):
    return await create_condition_service(payload, context.current_user, context.db)


@router.get(
    "/",
    response_model=list[ConditionResponse],
    summary="Get all conditions.",
    status_code=200,
)
async def get_conditions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    context: CommonContext = Depends(get_common_context),
):
    return await get_all_conditions_service(
        skip, limit, context.current_user, context.db
    )


@router.get(
    "/{condition_id}",
    response_model=ConditionResponse,
    summary="Get condition by its ID.",
    status_code=200,
)
async def get_condition_by_id(
    condition_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await get_condition_service(
            condition_id, context.current_user, context.db
        )
    except ConditionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Condition not found.") from err


@router.patch(
    "/{condition_id}",
    response_model=ConditionResponse,
    summary="Update condition by ID.",
    status_code=200,
)
async def update_condition(
    condition_id: uuid.UUID,
    payload: ConditionUpdate,
    context: CommonContext = Depends(get_common_context),
):
    try:
        return await update_condition_service(
            condition_id, payload, context.current_user, context.db
        )
    except ConditionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Condition not found.") from err


@router.delete(
    "/{condition_id}",
    response_model=ConditionDeleteResponse,
    summary="Delete condition by ID.",
    status_code=200,
)
async def delete_condition(
    condition_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await delete_condition_service(
            condition_id, context.current_user, context.db
        )
    except ConditionNotFoundError as err:
        raise HTTPException(status_code=404, detail="Condition not found.") from err
