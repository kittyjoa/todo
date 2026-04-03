"""Todo CRUD router — /api/todos endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from app.database import (
    get_db,
    fetch_all_todos,
    fetch_dates_with_todos,
    create_todo,
    fetch_todo_by_id,
    update_todo,
    delete_todo,
)
from app.models import TodoCreate, TodoUpdate, TodoResponse
import aiosqlite

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("/dates", response_model=list[str])
async def list_dates(db: aiosqlite.Connection = Depends(get_db)):
    """Return all dates that have at least one todo (YYYY-MM-DD list)."""
    return await fetch_dates_with_todos(db)


@router.get("/", response_model=list[TodoResponse])
async def list_todos(
    date: Optional[str] = Query(None, description="Filter by due_date (YYYY-MM-DD)"),
    db: aiosqlite.Connection = Depends(get_db),
):
    """Return todos, optionally filtered by date."""
    return await fetch_all_todos(db, due_date=date)


@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo_endpoint(
    payload: TodoCreate, db: aiosqlite.Connection = Depends(get_db)
):
    """Create a new todo. Returns 422 if title is empty or due_date invalid."""
    return await create_todo(db, payload.title, payload.due_date)


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo_endpoint(
    todo_id: int,
    payload: TodoUpdate,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Update title and/or completed state. Returns 400 if no fields, 404 if not found."""
    if payload.title is None and payload.completed is None:
        raise HTTPException(status_code=400, detail="수정할 필드를 하나 이상 제공해주세요")

    existing = await fetch_todo_by_id(db, todo_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")

    return await update_todo(db, todo_id, payload.title, payload.completed)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo_endpoint(
    todo_id: int, db: aiosqlite.Connection = Depends(get_db)
):
    """Delete a todo by id. Returns 204 on success, 404 if not found."""
    deleted = await delete_todo(db, todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")
    return Response(status_code=204)
