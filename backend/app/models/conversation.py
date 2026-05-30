from sqlalchemy import Column, Integer, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), default="新对话")
    status = Column(String(16), default="active")
    intent_type = Column(String(64), default="")
    sentiment_trend = Column(String(16), default="neutral")
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="conversation")
