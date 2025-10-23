from pydantic import BaseModel, Field

from app.modules.admin_handlers.enums.RecipientsEnum import RecipientsEnum


class BroadcastingSchema(BaseModel):
    message: str = Field(..., description="The message to be broadcasted to recipients")
    recipients: list[RecipientsEnum] = Field(
        ..., description="List of recipient user IDs"
    )
    photo: str | None = Field(
        None, description="Optional photo URL to be sent with the message"
    )
