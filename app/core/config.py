from pydantic_settings import BaseSettings, SettingsConfigDict


class YookassaSettings(BaseSettings):
    SHOP_ID: str
    SECRET_KEY: str
    RETURN_URL: str


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    BOT_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    REFRESH_SECRET_KEY: str
    SECRET_KEY: str

    CDEK_TEST_API_URL: str
    CDEK_TEST_ACCOUNT: str
    CDEK_TEST_SECURE_PASSWORD: str

    YOOKASSA: YookassaSettings

    @property
    def async_database_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    @property
    def sync_database_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )


settings = Settings()
