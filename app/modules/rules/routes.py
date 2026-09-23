import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import (
    RuleMustHaveConditionError,
    RuleNoLogicalOperator,
    RuleNotFoundError,
)
from app.database.dependencies import CommonContext, get_common_context
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
    payload: RuleCreate, context: CommonContext = Depends(get_common_context)
):
    return await create_rule_service(payload, context.current_user, context.db)


@router.get(
    "/",
    response_model=list[RuleResponse],
    summary="Get all user's rules.",
    status_code=200,
)
async def get_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    context: CommonContext = Depends(get_common_context),
):
    return await get_all_rules_service(skip, limit, context.current_user, context.db)


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Get rule by ID.",
    status_code=200,
)
async def get_rule_by_id(
    rule_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await get_rule_service(rule_id, context.current_user, context.db)
    except RuleNotFoundError as err:
        raise HTTPException(status_code=404, detail="Rule not found.") from err


@router.patch(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Update rule.",
    status_code=200,
)
async def update_rule(
    rule_id: uuid.UUID,
    payload: RuleUpdate,
    context: CommonContext = Depends(get_common_context),
):
    try:
        return await update_rule_service(
            rule_id, payload, context.current_user, context.db
        )
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
    rule_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await delete_rule_service(rule_id, context.current_user, context.db)
    except RuleNotFoundError as err:
        raise HTTPException(status_code=404, detail="Rule not found.") from err
