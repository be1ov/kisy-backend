from http.client import HTTPException

from fastapi import APIRouter, Depends

from app.core.dependencies.get_current_user import get_current_user
from app.modules.users.entities import UserEntity
from app.modules.users.schema.create import UserUpdateSchema
from app.modules.users.service import UserService

router = APIRouter()

@router.post("/update")
async def create_user(data: UserUpdateSchema, current_user: UserEntity = Depends(get_current_user), service: UserService = Depends()):
    try:
        user = await service.update_user(data, current_user)
        return  {
            "status": "success",
            "data": user
        }
    except Exception as e:
        raise HTTPException(e)


