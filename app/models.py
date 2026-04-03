"""Pydantic models for request/response validation."""
from typing import Optional
from pydantic import BaseModel, field_validator


class TodoCreate(BaseModel):
    """Request model for creating a new todo."""

    title: str
    due_date: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject empty strings."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("할 일 내용을 입력해주세요")
        return stripped

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_valid(cls, v: str) -> str:
        """Validate YYYY-MM-DD format."""
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        return v


class TodoUpdate(BaseModel):
    """Request model for updating a todo (all fields optional)."""

    title: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and reject empty title strings."""
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("할 일 내용을 입력해주세요")
        return stripped


class TodoResponse(BaseModel):
    """Response model for a todo item."""

    id: int
    title: str
    completed: bool
    position: int
    due_date: str
    created_at: str
