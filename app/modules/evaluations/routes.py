import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EvaluationNotFoundError
from app.database.dependencies import get_db
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
    user_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_evaluations_service(user_id, skip, limit, db)


@router.get(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Get evaluation by ID.",
    status_code=200,
)
async def get_evaluation_by_id(
    user_id: uuid.UUID, evaluation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    try:
        return await get_evaluation_service(user_id, evaluation_id, db)
    except EvaluationNotFoundError as err:
        raise HTTPException(status_code=404, detail="Evaluation not found.") from err
