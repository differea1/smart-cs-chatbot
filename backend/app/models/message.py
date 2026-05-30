from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    intent_type = Column(String(64), default="")
    sentiment = Column(String(16), default="neutral")
    confidence = Column(Float, default=0.0)
    knowledge_sources = Column(JSON, default=None)
    extra_data = Column("metadata", JSON, default=None)
    created_at = Column(DateTime, default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
