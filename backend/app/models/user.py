from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(128), unique=True, default="")
    nickname = Column(String(64), default="用户")
    avatar = Column(String(512), default="")
    phone = Column(String(20), default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
