from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services import auth as auth_service
from app.models import User

router = APIRouter()

@router.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

@router.post("/token", response_model=schemas.Token, tags=["auth"])
def login(form:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login(db, form.username, form.password)

@router.get("/me", tags=["auth"])
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}