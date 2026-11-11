from datetime import datetime
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel


class BotFileBase(BaseModel):
    bot_id: str
    content_type: Literal["file", "text", "embedding"]
    content: Union[
        str, dict
    ]  # Content can be a URL (file), text, or embedding reference
    embedding_id: Optional[str]  # Optional reference to Embeddings table
    meta: Optional[dict]  # Additional metadata


class BotFileCreate(BotFileBase):
    pass


class BotFile(BotFileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ExtractedFile(BaseModel):
    extracted_content: List
    meta_data: str
