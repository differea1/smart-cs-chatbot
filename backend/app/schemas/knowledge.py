from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KnowledgeItemCreate(BaseModel):
    category_id: int
    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=1)
    keywords: str = ""
    type: str = "qa"


class KnowledgeItemUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[str] = None
    type: Optional[str] = None
    is_published: Optional[int] = None


class KnowledgeItemResponse(BaseModel):
    id: int
    category_id: int
    title: str
    content: str
    keywords: str
    type: str
    is_published: int
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int
    children: list["KnowledgeCategoryResponse"] = []

    class Config:
        from_attributes = True
