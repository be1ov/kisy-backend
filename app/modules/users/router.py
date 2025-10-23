from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.users.entities import UserEntity
from app.modules.users.schema.create import UserUpdateSchema
from app.modules.users.service import UserService

router = APIRouter()


@router.get("/")
async def get_users(
    search: str = Query(
        None, description="Поиск по имени, фамилии, email или телефону"
    ),
    is_admin: bool = Query(None, description="Фильтр по админам"),
    signup_completed: bool = Query(
        None, description="Фильтр по завершению регистрации"
    ),
    limit: int = Query(100, description="Количество пользователей"),
    offset: int = Query(0, description="Смещение"),
    service: UserService = Depends(),
):
    """Получение списка всех пользователей с возможностью фильтрации"""
    try:
        users = await service.get_all()

        # Применяем фильтры
        if search:
            search_lower = search.lower()
            users = [
                user
                for user in users
                if (user.first_name and search_lower in user.first_name.lower())
                or (user.last_name and search_lower in user.last_name.lower())
                or (user.email and search_lower in user.email.lower())
                or (user.phone and search_lower in user.phone)
            ]

        if is_admin is not None:
            users = [user for user in users if user.is_admin == is_admin]

        if signup_completed is not None:
            users = [
                user for user in users if user.signup_completed == signup_completed
            ]

        # Применяем pagination
        total = len(users)
        users = users[offset : offset + limit]

        # Конвертируем в схемы
        user_schemas = [user.to_schema() for user in users]

        return user_schemas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user_by_id(user_id: str, service: UserService = Depends()):
    """Получение пользователя по ID"""
    try:
        user = await service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return user.to_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_user_by_id(
    user_id: str, data: UserUpdateSchema, service: UserService = Depends()
):
    """Обновление пользователя по ID"""
    try:
        user = await service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        updated_user = await service.update_user_by_id(user_id, data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return {"status": "success", "data": updated_user.to_schema()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def create_user(
    data: UserUpdateSchema,
    current_user: UserEntity = Depends(get_current_user),
    service: UserService = Depends(),
):
    try:
        user = await service.update_user(data, current_user)
        return {"status": "success", "data": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
