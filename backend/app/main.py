from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db, engine
from app.api import chat, knowledge, admin, auth

settings = get_settings()


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


@app.get("/")
def root():
    return {"message": "极米售后AI助手 API", "docs": "/docs"}


@app.get("/healthz")
def healthz():
    """轻量健康检查端点（不依赖数据库），适用于负载均衡器探活"""
    return {"status": "ok"}
