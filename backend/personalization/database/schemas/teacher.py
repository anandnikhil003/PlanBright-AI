from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TeacherBase(BaseModel):
    name: str
    email: str
    school_id: int
    teaching_style: Optional[str]
    preferences: Optional[dict]
    meta: Optional[dict]
    is_active: Optional[bool] = True


class TeacherCreate(TeacherBase):
    pass


class Teacher(TeacherBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
