from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class EmbeddingBase(BaseModel):
    content_id: str
    content_type: Literal["course_material", "historical_asset", "ai_generated_output", "bots"]
    embedding: List[float]  # Embedding as a list of floats
    meta: Optional[dict]  # Additional metadata


class EmbeddingCreate(EmbeddingBase):
    pass


class Embedding(EmbeddingBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
