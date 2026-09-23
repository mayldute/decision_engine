import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import EvaluationNotFoundError
from app.database.dependencies import CommonContext, get_common_context
from app.modules.evaluations.schemas import EvaluationListResponse, EvaluationResponse
from app.modules.evaluations.services import (
    get_all_evaluations_service,
    get_evaluation_service,
)

router = APIRouter(prefix="/evaluations", tags=["[evaluations] evaluations"])


@router.get(
    "/",
    response_model=list[EvaluationListResponse],
    summary="Get all user's evaluations",
    status_code=200,
)
async def get_evaluations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    context: CommonContext = Depends(get_common_context),
):
    return await get_all_evaluations_service(
        skip, limit, context.current_user, context.db
    )


@router.get(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Get evaluation by ID.",
    status_code=200,
)
async def get_evaluation_by_id(
    evaluation_id: uuid.UUID, context: CommonContext = Depends(get_common_context)
):
    try:
        return await get_evaluation_service(
            evaluation_id, context.current_user, context.db
        )
    except EvaluationNotFoundError as err:
        raise HTTPException(status_code=404, detail="Evaluation not found.") from err
