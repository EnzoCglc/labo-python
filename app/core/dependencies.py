from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Role, User

# Temporory add pending the creation of the /token route
Temp_user = "etudiant"

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.username == Temp_user))
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    return user

def require_manager(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.gestionnaire:
        raise HTTPException(status_code=403,detail="Insufficient permissions")
    return user