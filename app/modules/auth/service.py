import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt

import bcrypt
from fastapi.params import Depends

from app.core.config import settings
from app.modules.auth.schemas.access_token import AccessTokenSchema
from app.modules.auth.schemas.refresh_token import RefreshTokenSchema
from app.modules.auth.schemas.signup import SignupSchema
from app.modules.users.entities import UserEntity
from app.modules.users.service import UserService


class WrongInitData(ValueError):
    pass


class InvalidAccessToken(ValueError):
    pass


class AuthService:
    def __init__(self, users_service: UserService = Depends()):
        self.users_service = users_service

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def signup(self, data: SignupSchema) -> UserEntity:
        user = UserEntity(**data.model_dump())
        user.password = self.hash_password(data.password)
        return await self.users_service.save(user)

    @staticmethod
    def parse_init_data(init_data: str):
        parsed_qsl = urllib.parse.parse_qsl(init_data, strict_parsing=True)
        return dict(parsed_qsl)

    @staticmethod
    def validate_init_data_hash(parsed: dict, _hash: str):
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )

        secret_key = hmac.new(
            key=b"WebAppData", msg=settings.BOT_TOKEN.encode(), digestmod=hashlib.sha256
        )
        hmac_hash = hmac.new(secret_key.digest(), data_check_string.encode(), hashlib.sha256).hexdigest()

        if hmac_hash != _hash:
            return False

        return True

    async def process_init_data(self, init_data: str):
        parsed_data = self.parse_init_data(init_data)

        init_data_hash = parsed_data.pop("hash")
        validation_result = self.validate_init_data_hash(parsed_data, init_data_hash)

        if not validation_result:
            raise WrongInitData("Validation failed")

        user_json = parsed_data.get("user")
        try:
            user_data = json.loads(user_json)
        except (json.JSONDecodeError, KeyError):
            raise WrongInitData("Missing user_data")

        try:
            telegram_id = user_data.get("telegram_id")
        except KeyError:
            raise WrongInitData("Missing id")

        user = await self.users_service.get_by_id(telegram_id)
        if not user:
            user = await self.users_service.create_user(telegram_id)

        return user

    @staticmethod
    def generate_access_token(user: UserEntity) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = AccessTokenSchema(user_id=user.id, exp=expire)
        return jwt.encode(payload.model_dump(), settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def generate_refresh_token(user: UserEntity) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = RefreshTokenSchema(user_id=user.id, exp=expire)
        return jwt.encode(payload.model_dump(), settings.REFRESH_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_access_token(token: str) -> AccessTokenSchema | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return AccessTokenSchema(**payload)
        except Exception:
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> RefreshTokenSchema | None:
        try:
            payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=["HS256"])
            return RefreshTokenSchema(**payload)
        except Exception:
            return None