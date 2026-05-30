from sqlalchemy import Column, Integer, String, Text, Integer, SmallInteger, DateTime, ForeignKey, func
from app.core.database import Base


class KnowledgeCategory(Base):
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    parent_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=False)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(String(512), default="")
    type = Column(String(32), default="qa")
    is_published = Column(Integer, default=1)
    view_count = Column(Integer, default=0)
    embedding_id = Column(String(128), default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(String(512), default="")
    created_at = Column(DateTime, default=func.now())


class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    reason = Column(String(64), default="user_request")
    handled_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=func.now())
