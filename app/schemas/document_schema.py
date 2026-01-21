from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CreateDocumentForm(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class DocumentOut(BaseModel):
    id: int
    owner_id: int
    title: str
    file_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailOut(DocumentOut):
    signers_count: int
    comments_count: int

    model_config = ConfigDict(from_attributes=True)
