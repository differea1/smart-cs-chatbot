from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.admin import LoginRequest, LoginResponse
from app.models.admin import AdminUser
from app.core.database import get_db
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(
        AdminUser.username == req.username,
        AdminUser.is_active == 1,
    ).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token({"sub": user.username, "role": user.role})
    return LoginResponse(
        access_token=token,
        username=user.username,
        role=user.role,
    )
