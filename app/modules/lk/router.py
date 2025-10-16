from fastapi import APIRouter, Depends

from app.core.dependencies.get_current_user import get_current_user
from app.modules.lk.schemas.responses.lk_data_response_schema import (
    LKDataResponseSchema,
)
from app.modules.lk.service import LKService
from app.modules.users.entities import UserEntity

router = APIRouter()


@router.get("/")
async def lk_root(
    service: LKService = Depends(), user: UserEntity = Depends(get_current_user)
) -> LKDataResponseSchema:
    response = await service.get_info(user)
    return response
