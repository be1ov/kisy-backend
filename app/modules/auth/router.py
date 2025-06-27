from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.core.dependencies.get_current_user import get_current_user
from app.modules.auth.service import AuthService, WrongInitData
from app.modules.auth.schemas.signup import SignupSchema
from app.modules.users.entities import UserEntity
from app.modules.users.service import UserService

router = APIRouter()


@router.post('/signup')
async def signup(data: SignupSchema, users_service: UserService = Depends(),
                 current_user: UserEntity = Depends(get_current_user)):
    await users_service.finish_signup(data, current_user)
    return {
        "status": "success"
    }


@router.post('/telegram')
async def telegram_auth(init_data: str, auth_service: AuthService = Depends()):
    try:
        user = await auth_service.process_init_data(init_data)
        if user is None:
            raise HTTPException(status_code=404, detail="Invalid user")

        access_token = auth_service.generate_access_token(user)
        refresh_token = auth_service.generate_refresh_token(user)

        return {
            "status": "success",
            "data": {
                "access": access_token,
                "refresh": refresh_token
            }
        }
    except WrongInitData as e:
        raise HTTPException(status_code=403, detail="Auth failed")


@router.post('/refresh')
async def refresh_token(refresh_token: str, auth_service: AuthService = Depends(),
                        users_service: UserService = Depends()):
    payload = auth_service.verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    user = await users_service.get_by_id(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = auth_service.generate_access_token(user)

    return {
        "status": "success",
        "data": {
            "access": access_token,
        }
    }


@router.get("/me")
async def me(user: UserEntity = Depends(get_current_user)):
    return {
        "status": "success",
        "data": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "signup_completed": user.signup_completed,
        }
    }
