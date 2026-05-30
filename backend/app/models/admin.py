from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, ForeignKey, func
from app.core.database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), default="operator")
    is_active = Column(Integer, default=1)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SystemPrompt(Base):
    __tablename__ = "system_prompts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    version = Column(String(16), default="1.0")
    intent_type = Column(String(64), default="base")
    content = Column(Text, nullable=False)
    is_active = Column(Integer, default=0)
    created_by = Column(BigInteger, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
