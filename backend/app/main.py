import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db, engine
from app.api import chat, knowledge, admin, auth

settings = get_settings()
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理后台"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])


# Serve frontend static files in production
if os.path.exists(STATIC_DIR) and os.path.isdir(STATIC_DIR):
    # Mount static asset directories
    for folder in ["assets", "icons"]:
        path = os.path.join(STATIC_DIR, folder)
        if os.path.exists(path):
            app.mount(f"/{folder}", StaticFiles(directory=path), name=folder)

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    # SPA fallback: serve index.html for any unhandled GET request
    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.isfile(index_path) and not request.url.path.startswith("/api"):
                return FileResponse(index_path)
        return response
else:
    @app.get("/")
    def root():
        return {"message": "极米售后AI助手 API", "docs": "/docs"}


@app.get("/healthz")
def healthz():
    """轻量健康检查端点（不依赖数据库），适用于负载均衡器探活"""
    return {"status": "ok"}
