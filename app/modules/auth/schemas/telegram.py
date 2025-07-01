from pydantic import BaseModel


class TelegramSchema(BaseModel):
    init_data: str