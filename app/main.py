"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db
from app.routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await init_db()
    yield


app = FastAPI(title="TodoList", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(todos.router)


@app.get("/")
async def index():
    """Serve the main SPA page."""
    return FileResponse("app/templates/index.html")
