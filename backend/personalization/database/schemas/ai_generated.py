from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AIGeneratedOutputBase(BaseModel):
    teacher_id: str
    type: str
    content: dict
    feedback_notes: Optional[str]
    meta: Optional[dict]


class AIGeneratedOutputCreate(AIGeneratedOutputBase):
    pass


class AIGeneratedOutput(AIGeneratedOutputBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
