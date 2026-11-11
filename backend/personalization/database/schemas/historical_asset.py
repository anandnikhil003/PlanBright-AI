from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class HistoricalAssetBase(BaseModel):
    teacher_id: str
    name: str
    type: Literal["lesson plan", "worksheet"]
    content: dict
    content_type: Literal["file", "text"]
    meta: Optional[dict]
    is_active: Optional[bool] = True


class HistoricalAssetCreate(HistoricalAssetBase):
    pass


class HistoricalAsset(HistoricalAssetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
