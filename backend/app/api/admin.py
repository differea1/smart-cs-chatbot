from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.schemas.admin import DashboardResponse
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.knowledge import FeedbackRecord
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


def require_admin(user: dict = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total = db.query(func.count(Conversation.id)).scalar() or 0
    today_count = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= today
    ).scalar() or 0

    avg_rating = db.query(func.avg(FeedbackRecord.rating)).scalar() or 0.0

    complaint_count = db.query(func.count(Conversation.id)).filter(
        Conversation.intent_type == "complaint"
    ).scalar() or 0

    return DashboardResponse(
        total_conversations=total,
        today_conversations=today_count,
        avg_satisfaction=round(float(avg_rating), 2),
        escalation_rate=round(complaint_count / max(total, 1) * 100, 1),
    )


@router.get("/conversations")
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Conversation).order_by(Conversation.updated_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [
            {
                "id": c.id,
                "user_id": c.user_id,
                "title": c.title,
                "status": c.status,
                "intent_type": c.intent_type,
                "sentiment_trend": c.sentiment_trend,
                "message_count": c.message_count,
                "created_at": c.created_at.isoformat() if c.created_at else "",
            }
            for c in items
        ],
    }


@router.get("/messages/{conv_id}")
async def get_messages(
    conv_id: int,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    msgs = db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.created_at.asc()).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "intent_type": m.intent_type,
            "sentiment": m.sentiment,
            "confidence": m.confidence,
            "created_at": m.created_at.isoformat() if m.created_at else "",
        }
        for m in msgs
    ]
