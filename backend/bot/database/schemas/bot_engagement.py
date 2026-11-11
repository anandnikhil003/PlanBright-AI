from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BotEngagementBase(BaseModel):
    bot_id: str
    user_id: str
    messages_sent: str
    likes: bool


class BotEngagementCreate(BotEngagementBase):
    pass


class BotEngagement(BotEngagementBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
