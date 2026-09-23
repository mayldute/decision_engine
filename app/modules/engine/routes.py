from fastapi import APIRouter, Depends

from app.database.dependencies import CommonContext, get_common_context
from app.modules.engine.services import engine_service

router = APIRouter(prefix="/engine", tags=["[engine] engine"])


@router.post("/", summary="Rule engine", status_code=200)
async def rules_engine(
    input_data: dict, context: CommonContext = Depends(get_common_context)
) -> dict:
    return await engine_service(input_data, context.current_user, context.db)
