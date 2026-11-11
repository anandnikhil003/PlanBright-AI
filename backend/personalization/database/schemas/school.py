from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SchoolBase(BaseModel):
    name: str
    curriculum: Optional[List[str]]
    pedagogy: Optional[List[str]]
    location: Optional[str]
    meta: Optional[dict]
    is_active: Optional[bool] = True


class SchoolCreate(SchoolBase):
    pass


class School(SchoolBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
