from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.modules.auth.schemas.signup import SignupSchema
from app.modules.users.entities import UserEntity


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

    async def create_user(self, telegram_id: str):
        user = UserEntity(telegram_id=telegram_id)
        self._db.add(user)
        await self._db.commit()

    async def save(self, user: UserEntity) -> UserEntity:
        self._db.add(user)
        await self._db.commit()
        return user

    async def finish_signup(self, data: SignupSchema, user: UserEntity) -> UserEntity:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.email = data.email
        user.phone = data.phone
        user.birth_date = data.birth_date

        user.signup_completed = True

        self._db.add(user)
        await self._db.commit()
        return user