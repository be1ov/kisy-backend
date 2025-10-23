from datetime import datetime
from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm.sync import update

from app.core.db.session import get_session
from app.modules.auth.schemas.signup import SignupSchema
from app.modules.users.entities import UserEntity
from app.modules.users.schema.create import UserUpdateSchema


class UserService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def get_by_id(self, _id: str):
        stmt = select(UserEntity).where(UserEntity.id == _id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def get_by_telegram_id(self, telegram_id: str):
        stmt = select(UserEntity).where(UserEntity.telegram_id == telegram_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def get_all(self):
        stmt = select(UserEntity)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, telegram_id: int, username: str | None = None):
        user = UserEntity(telegram_id=telegram_id, username=username)
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def save(self, user: UserEntity) -> UserEntity:
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def finish_signup(self, data: SignupSchema, user: UserEntity) -> UserEntity:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.email = data.email
        user.phone = data.phone
        # Конвертируем date в datetime
        if data.birth_date:
            user.birth_date = datetime.combine(data.birth_date, datetime.min.time())

        user.signup_completed = True

        self._db.add(user)
        await self._db.commit()
        return user

    async def update_user(self, data: UserUpdateSchema, user: UserEntity):
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.email is not None:
            user.email = data.email
        if data.phone is not None:
            user.phone = data.phone
        if data.is_admin is not None:
            user.is_admin = data.is_admin
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def update_user_by_id(self, user_id: str, data: UserUpdateSchema):
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.email is not None:
            user.email = data.email
        if data.phone is not None:
            user.phone = data.phone
        if data.is_admin is not None:
            user.is_admin = data.is_admin
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user
