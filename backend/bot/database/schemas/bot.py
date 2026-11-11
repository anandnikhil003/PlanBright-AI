from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BotBase(BaseModel):
    bot_id: Optional[str] = None
    name: str
    description: str
    persona: str  # Example values: 'Teachers Assistant', 'Students Assistant'
    purpose: str
    icon: Optional[str]
    color_palette: Optional[str]
    gpt_model: Optional[str] = "gpt-4o-mini"
    is_published: Optional[bool] = False
    scope: str  # Example values: 'school', 'unconstrained'


class BotCreate(BotBase):
    pass


class Bot(BotBase):
    id: str
    created_by: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BotDetails(BaseModel):
    bot_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    likes_count: int
    message_count: int
    unique_user_count: int
    is_published: bool
    color_palette: str
    gpt_model: str
    persona: str
    purpose: str
    owner_flag: bool
    is_favourite: bool
    icon: Optional[str] = None


class MyBotDetails(BotDetails):
    recently_added_tag: bool


class BotEditData(BaseModel):
    name: str
    description: str
    persona: str
    purpose: Optional[str] = None
    icon: Optional[str] = None
    color_palette: str
    gpt_model: str
    is_published: bool
    created_by: str
    user_id: str


class CreateBotInfo(BaseModel):
    id: str
    bot_type: str


# class UpdateBotInfo(BaseModel):
#     name: str
#     description: str
#     persona: str  # Example values: 'Teachers Assistant', 'Students Assistant'
#     purpose: str
#     icon: Optional[str]
#     color_palette: Optional[str]
#     gpt_model: Optional[str] = "gpt-4o-mini"
#     scope: str  # Example values: 'school', 'unconstrained'


class CreateIframeInfo(BaseModel):
    iframe_id: str
    bot_id: str


class IframeInfoRequest(BaseModel):
    bot_id: str


class IframeBotHistory(BaseModel):
    iframe_id: str
    finger_print_id: str
