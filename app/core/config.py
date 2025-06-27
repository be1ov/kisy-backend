from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    BOT_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()