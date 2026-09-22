import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    RuleMustHaveConditionError,
    RuleNoLogicalOperator,
    RuleNotFoundError,
)
from app.database.dependencies import get_db
from app.modules.rules.schemas import (
    RuleCreate,
    RuleDeleteResponse,
    RuleResponse,
    RuleUpdate,
)
from app.modules.rules.services import (
    create_rule_service,
    delete_rule_service,
    get_all_rules_service,
    get_rule_service,
    update_rule_service,
)

router = APIRouter(prefix="/rules", tags=["[rules] rules"])


@router.post(
    "/",
    response_model=RuleResponse,
    summary="Create rule.",
    status_code=201,
)
async def create_rule(
    user_id: uuid.UUID, payload: RuleCreate, db: AsyncSession = Depends(get_db)
):
    return await create_rule_service(user_id, payload, db)


@router.get(
    "/",
    response_model=list[RuleResponse],
    summary="Get all user's rules.",
    status_code=200,
)
async def get_rules(
    user_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_rules_service(user_id, skip, limit, db)


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Get rule by ID.",
    status_code=200,
)
async def get_rule_by_id(
    user_id: uuid.UUID, rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    try:
        return await get_rule_service(user_id, rule_id, db)
    except RuleNotFoundError as err:
        raise HTTPException(status_code=404, detail="Rule not found.") from err


@router.patch(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Update rule.",
    status_code=200,
)
async def update_rule(
    user_id: uuid.UUID,
    rule_id: uuid.UUID,
    payload: RuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_rule_service(user_id, rule_id, payload, db)
    except RuleMustHaveConditionError as err:
        raise HTTPException(
            status_code=400, detail="At least one condition must be provided."
        ) from err
    except RuleNoLogicalOperator as err:
        raise HTTPException(
            status_code=400,
            detail=(
                "Rule must contain a logical operator if it contains "
                "more than one condition."
            ),
        ) from err
    except RuleNotFoundError as err:
        raise HTTPException(status_code=404, detail="Rule not found.") from err


@router.delete(
    "/{rule_id}",
    response_model=RuleDeleteResponse,
    summary="Delete rule.",
    status_code=200,
)
async def delete_rule(
    user_id: uuid.UUID, rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    try:
        return await delete_rule_service(user_id, rule_id, db)
    except RuleNotFoundError as err:
        raise HTTPException(status_code=404, detail="Rule not found.") from err
