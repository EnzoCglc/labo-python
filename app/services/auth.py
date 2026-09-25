from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models import User

def login(db: Session, username: str, password: str) -> dict:
    user = db.scalar(select(User).where(User.username == username))
    
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}