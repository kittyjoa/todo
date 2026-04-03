"""Database access layer — only module allowed to import aiosqlite."""
import aiosqlite

DATABASE_PATH = "todo.db"


async def init_db() -> None:
    """Create the todos table and migrate schema if needed."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                position INTEGER NOT NULL DEFAULT 0,
                due_date TEXT NOT NULL DEFAULT (date('now', 'localtime')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # 기존 DB 마이그레이션: due_date 컬럼 없으면 추가
        async with db.execute("PRAGMA table_info(todos)") as cursor:
            columns = {row[1] async for row in cursor}
        if "due_date" not in columns:
            await db.execute(
                "ALTER TABLE todos ADD COLUMN due_date TEXT NOT NULL DEFAULT '1970-01-01'"
            )
        await db.commit()


async def get_db():
    """Async generator that yields a configured aiosqlite connection."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def fetch_all_todos(db: aiosqlite.Connection, due_date: str | None = None) -> list[dict]:
    """Return todos, optionally filtered by due_date (YYYY-MM-DD)."""
    if due_date:
        async with db.execute(
            "SELECT * FROM todos WHERE due_date = ? ORDER BY position ASC, created_at DESC",
            (due_date,),
        ) as cursor:
            rows = await cursor.fetchall()
    else:
        async with db.execute(
            "SELECT * FROM todos ORDER BY due_date ASC, position ASC, created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def fetch_dates_with_todos(db: aiosqlite.Connection) -> list[str]:
    """Return distinct due_dates that have at least one todo."""
    async with db.execute(
        "SELECT DISTINCT due_date FROM todos ORDER BY due_date ASC"
    ) as cursor:
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def create_todo(db: aiosqlite.Connection, title: str, due_date: str) -> dict:
    """Insert a new todo and return the created record."""
    async with db.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM todos WHERE due_date = ?",
        (due_date,),
    ) as cursor:
        row = await cursor.fetchone()
    position = row[0]

    async with db.execute(
        "INSERT INTO todos (title, completed, position, due_date) VALUES (?, 0, ?, ?)",
        (title, position, due_date),
    ) as cursor:
        todo_id = cursor.lastrowid

    await db.commit()
    return await fetch_todo_by_id(db, todo_id)


async def fetch_todo_by_id(db: aiosqlite.Connection, todo_id: int) -> dict | None:
    """Return a single todo by id, or None if not found."""
    async with db.execute(
        "SELECT * FROM todos WHERE id = ?", (todo_id,)
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None


async def update_todo(
    db: aiosqlite.Connection,
    todo_id: int,
    title: str | None = None,
    completed: bool | None = None,
) -> dict | None:
    """Update title and/or completed for a todo. Returns updated record or None."""
    if title is not None and completed is not None:
        await db.execute(
            "UPDATE todos SET title = ?, completed = ? WHERE id = ?",
            (title, completed, todo_id),
        )
    elif title is not None:
        await db.execute(
            "UPDATE todos SET title = ? WHERE id = ?",
            (title, todo_id),
        )
    elif completed is not None:
        await db.execute(
            "UPDATE todos SET completed = ? WHERE id = ?",
            (completed, todo_id),
        )
    else:
        return await fetch_todo_by_id(db, todo_id)

    await db.commit()
    return await fetch_todo_by_id(db, todo_id)


async def delete_todo(db: aiosqlite.Connection, todo_id: int) -> bool:
    """Delete a todo by id. Returns True if a row was deleted."""
    async with db.execute(
        "DELETE FROM todos WHERE id = ?", (todo_id,)
    ) as cursor:
        deleted = cursor.rowcount > 0
    await db.commit()
    return deleted
