import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User


class ChatService:
    async def get_or_create_session(self, db: Session, user_id: int, session_id: str | None) -> dict:
        if session_id:
            conv = db.query(Conversation).filter(Conversation.id == int(session_id)).first()
            if conv:
                return {"id": conv.id, "history": self._get_history(db, conv.id)}

        # 匿名用户自动创建
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id if user_id > 0 else None, openid=str(uuid.uuid4())[:16])
            db.add(user)
            db.commit()
            db.refresh(user)

        conv = Conversation(user_id=user.id, title="新对话")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return {"id": conv.id, "history": []}

    def _get_history(self, db: Session, conv_id: int) -> list[dict]:
        msgs = (
            db.query(Message)
            .filter(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        return [{"role": m.role, "content": m.content} for m in msgs]

    async def save_messages(
        self,
        db: Session,
        session_id: int,
        user_message: str,
        ai_response: str,
        intent: str,
        sentiment: str,
        confidence: float,
        knowledge_sources: list[str],
    ) -> int:
        # 保存用户消息
        user_msg = Message(
            conversation_id=session_id,
            role="user",
            content=user_message,
            intent_type=intent,
            sentiment=sentiment,
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # 保存AI消息
        ai_msg = Message(
            conversation_id=session_id,
            role="assistant",
            content=ai_response,
            intent_type=intent,
            sentiment=sentiment,
            confidence=confidence,
            knowledge_sources=knowledge_sources,
        )
        db.add(ai_msg)

        # 更新会话
        conv = db.query(Conversation).filter(Conversation.id == session_id).first()
        if conv:
            conv.message_count = (conv.message_count or 0) + 2
            conv.intent_type = intent
            conv.sentiment_trend = sentiment
            conv.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(ai_msg)
        return ai_msg.id
