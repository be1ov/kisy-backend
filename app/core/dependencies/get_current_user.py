from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request

from app.modules.auth.schemas.access_token import AccessTokenSchema
from app.modules.auth.service import AuthService
from app.modules.users.service import UserService


async def get_current_user(request: Request, users_service: UserService = Depends()):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Bearer Token')

    token = auth.split(" ")[1]
    payload: AccessTokenSchema | None = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    user = await users_service.get_by_id(payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user