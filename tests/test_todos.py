"""API tests for todo operations."""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
import app.database as db_module
from app.database import init_db

TODAY = "2026-04-03"
OTHER_DATE = "2026-04-04"


@pytest_asyncio.fixture(autouse=True)
async def setup_db(tmp_path):
    """Isolate each test with a fresh temporary database."""
    test_db_path = str(tmp_path / "test.db")
    db_module.DATABASE_PATH = test_db_path
    await init_db()
    yield
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest_asyncio.fixture
async def client():
    """Async HTTP client using ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── 목록 조회 ─────────────────────────────────────────────

async def test_list_todos_empty(client):
    """빈 DB에서 목록 조회 시 200 + 빈 배열."""
    res = await client.get(f"/api/todos/?date={TODAY}")
    assert res.status_code == 200
    assert res.json() == []


async def test_list_todos_with_items(client):
    """항목이 있을 때 목록 조회 시 개수 확인."""
    await client.post("/api/todos/", json={"title": "첫 번째", "due_date": TODAY})
    await client.post("/api/todos/", json={"title": "두 번째", "due_date": TODAY})
    res = await client.get(f"/api/todos/?date={TODAY}")
    assert res.status_code == 200
    assert len(res.json()) == 2


async def test_list_todos_date_filter(client):
    """날짜 필터 — 다른 날짜 항목은 보이지 않음."""
    await client.post("/api/todos/", json={"title": "오늘", "due_date": TODAY})
    await client.post("/api/todos/", json={"title": "내일", "due_date": OTHER_DATE})
    res = await client.get(f"/api/todos/?date={TODAY}")
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "오늘"


# ── 할 일 추가 ────────────────────────────────────────────

async def test_create_todo_success(client):
    """정상 추가 시 201 + 반환값."""
    res = await client.post("/api/todos/", json={"title": "운동하기", "due_date": TODAY})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "운동하기"
    assert data["completed"] is False
    assert data["due_date"] == TODAY


async def test_create_todo_empty_title(client):
    """빈 제목 시 422."""
    res = await client.post("/api/todos/", json={"title": "", "due_date": TODAY})
    assert res.status_code == 422


async def test_create_todo_whitespace(client):
    """공백만 있는 제목 시 422."""
    res = await client.post("/api/todos/", json={"title": "   ", "due_date": TODAY})
    assert res.status_code == 422


async def test_create_todo_strips_whitespace(client):
    """앞뒤 공백 자동 제거."""
    res = await client.post("/api/todos/", json={"title": "  독서  ", "due_date": TODAY})
    assert res.status_code == 201
    assert res.json()["title"] == "독서"


# ── 완료 토글 ─────────────────────────────────────────────

async def test_toggle_todo_complete(client):
    """미완료 → 완료."""
    created = (await client.post("/api/todos/", json={"title": "테스트", "due_date": TODAY})).json()
    res = await client.patch(f"/api/todos/{created['id']}", json={"completed": True})
    assert res.status_code == 200
    assert res.json()["completed"] is True


async def test_toggle_todo_incomplete(client):
    """완료 → 미완료."""
    created = (await client.post("/api/todos/", json={"title": "테스트", "due_date": TODAY})).json()
    await client.patch(f"/api/todos/{created['id']}", json={"completed": True})
    res = await client.patch(f"/api/todos/{created['id']}", json={"completed": False})
    assert res.status_code == 200
    assert res.json()["completed"] is False


# ── 제목 수정 ─────────────────────────────────────────────

async def test_update_todo_title(client):
    """제목 수정 후 새 제목 반환."""
    created = (await client.post("/api/todos/", json={"title": "원래", "due_date": TODAY})).json()
    res = await client.patch(f"/api/todos/{created['id']}", json={"title": "수정됨"})
    assert res.status_code == 200
    assert res.json()["title"] == "수정됨"


async def test_update_todo_empty_title(client):
    """빈 제목으로 수정 시 422."""
    created = (await client.post("/api/todos/", json={"title": "원래", "due_date": TODAY})).json()
    res = await client.patch(f"/api/todos/{created['id']}", json={"title": ""})
    assert res.status_code == 422


async def test_update_todo_not_found(client):
    """없는 id 수정 시 404."""
    res = await client.patch("/api/todos/999", json={"title": "없음"})
    assert res.status_code == 404


async def test_update_todo_no_fields(client):
    """필드 없이 PATCH 시 400."""
    created = (await client.post("/api/todos/", json={"title": "테스트", "due_date": TODAY})).json()
    res = await client.patch(f"/api/todos/{created['id']}", json={})
    assert res.status_code == 400


# ── 삭제 ──────────────────────────────────────────────────

async def test_delete_todo_success(client):
    """삭제 후 204 + 목록에서 제거."""
    created = (await client.post("/api/todos/", json={"title": "삭제", "due_date": TODAY})).json()
    res = await client.delete(f"/api/todos/{created['id']}")
    assert res.status_code == 204
    todos = (await client.get(f"/api/todos/?date={TODAY}")).json()
    assert len(todos) == 0


async def test_delete_todo_not_found(client):
    """없는 id 삭제 시 404."""
    res = await client.delete("/api/todos/999")
    assert res.status_code == 404


# ── 날짜 목록 ─────────────────────────────────────────────

async def test_dates_with_todos(client):
    """할 일이 있는 날짜만 반환."""
    await client.post("/api/todos/", json={"title": "A", "due_date": TODAY})
    await client.post("/api/todos/", json={"title": "B", "due_date": OTHER_DATE})
    res = await client.get("/api/todos/dates")
    assert res.status_code == 200
    assert TODAY in res.json()
    assert OTHER_DATE in res.json()
