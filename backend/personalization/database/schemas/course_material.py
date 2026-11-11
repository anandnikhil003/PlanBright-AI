from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class CourseMaterialBase(BaseModel):
    school_id: str
    name: str
    content: dict
    content_type: Literal["file", "text", "embedding"]
    meta: Optional[dict]


class CourseMaterialCreate(CourseMaterialBase):
    pass


class CourseMaterial(CourseMaterialBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
