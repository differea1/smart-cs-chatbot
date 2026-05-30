import json
import re
import time
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse, FeedbackRequest
from app.services.chat_service import ChatService
from app.services.intent_service import IntentService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.sentiment_service import SentimentService
from app.services.prompt_service import PromptBuilder
from app.core.database import get_db
from app.core.config import get_settings
from app.models.message import Message

router = APIRouter()
settings = get_settings()

# Simple in-memory rate limiter
_rate_limit_store: dict[str, list[float]] = {}

HTML_TAG_RE = re.compile(r"<[^>]*>")


def _sanitize_input(text: str) -> str:
    """Strip HTML tags from user input to prevent XSS."""
    return HTML_TAG_RE.sub("", text)


def _check_rate_limit(ip: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    window = 60.0  # 1 minute window
    limit = settings.RATE_LIMIT_PER_MINUTE

    if ip not in _rate_limit_store:
        _rate_limit_store[ip] = []

    # Remove timestamps outside the window
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < window]

    if len(_rate_limit_store[ip]) >= limit:
        return False

    _rate_limit_store[ip].append(now)
    return True


@router.post("/send")
async def send_message(req: ChatRequest, request: Request, db: Session = Depends(get_db)):
    # Rate limit check
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        async def rate_limited():
            yield f"data: {json.dumps({'delta': '请求过于频繁，请稍后重试。'})}\n\n"
        return StreamingResponse(
            rate_limited(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # Sanitize input
    sanitized_message = _sanitize_input(req.message)
    if not sanitized_message.strip():
        async def empty():
            yield f"data: {json.dumps({'delta': '请输入有效的问题。'})}\n\n"
        return StreamingResponse(
            empty(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    chat_svc = ChatService()
    intent_svc = IntentService()
    rag_svc = RAGService()
    llm_svc = LLMService()
    sentiment_svc = SentimentService()
    prompt_builder = PromptBuilder()

    # 1. 获取或创建会话
    session = await chat_svc.get_or_create_session(db, req.user_id, req.session_id)

    # 2. 意图识别
    intent, intent_conf = await intent_svc.classify(sanitized_message)

    # 3. 情绪分析
    sentiment = await sentiment_svc.analyze(sanitized_message)

    # 4. RAG 检索
    rag_results = await rag_svc.search(sanitized_message, top_k=3)

    # 5. 组装提示词 + 对话历史
    messages = prompt_builder.build(
        intent=intent,
        rag_results=rag_results,
        conversation_history=session["history"],
        sentiment=sentiment,
    )
    # 添加当前用户消息
    messages.append({"role": "user", "content": sanitized_message})

    # 6. 流式响应
    async def generate():
        full_response = ""
        try:
            async for chunk in llm_svc.chat_stream(messages):
                full_response += chunk
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
        except Exception as e:
            full_response = f"抱歉，服务暂时不可用，请稍后重试。（错误：{str(e)}）"
            yield f"data: {json.dumps({'delta': full_response})}\n\n"

        # 7. 保存消息
        msg_id = await chat_svc.save_messages(
            db=db,
            session_id=session["id"],
            user_message=sanitized_message,
            ai_response=full_response,
            intent=intent,
            sentiment=sentiment,
            confidence=intent_conf,
            knowledge_sources=[r["id"] for r in rag_results],
        )

        done_data = ChatResponse(
            session_id=str(session["id"]),
            message_id=msg_id,
            intent=intent,
            sentiment=sentiment,
            confidence=intent_conf,
            knowledge_sources=[r["id"] for r in rag_results],
        )
        yield f"event: done\ndata: {done_data.model_dump_json()}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}")
async def get_history(session_id: int, db: Session = Depends(get_db)):
    chat_svc = ChatService()
    history = chat_svc._get_history(db, session_id)
    return {"session_id": session_id, "messages": history}


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    from app.models.knowledge import FeedbackRecord
    fb = FeedbackRecord(message_id=req.message_id, rating=req.rating, comment=req.comment)
    db.add(fb)
    db.commit()
    return {"status": "ok"}


@router.get("/health")
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(db.bind.dialect.do_ping(None) if hasattr(db.bind.dialect, 'do_ping') else __import__('sqlalchemy').text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "db_ok": db_ok}
