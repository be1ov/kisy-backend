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

    async def create_user(self, telegram_id: int):
        user = UserEntity(telegram_id=telegram_id)
        self._db.add(user)
        await self._db.commit()
        return user

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

    async def update_user(self, data: UserUpdateSchema, user: UserEntity):
        async with self._db.begin() as conn:
            user.first_name = data.first_name
            user.last_name = data.last_name
            user.email = data.email
            user.phone = data.phone
            self._db.add(user)
            await self._db.refresh(user)
        return user
