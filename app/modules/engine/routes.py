import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.modules.engine.services import engine_service

router = APIRouter(prefix="/engine", tags=["[engine] engine"])


@router.post("/", summary="Rule engine", status_code=200)
async def rules_engine(
    user_id: uuid.UUID, input_data: dict, db: AsyncSession = Depends(get_db)
) -> dict:
    return await engine_service(user_id, input_data, db)
