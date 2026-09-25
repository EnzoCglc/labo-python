import jwt 

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ALGORITHM, SECRET_KEY
from app.models import Role, User

# Extract token in header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)) -> User:
    
    credentials_error = HTTPException(status_code=401, detail="Token invalid or expired ", headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise credentials_error
    
    username = payload.get("sub")
    if not username:
        raise credentials_error
    
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise credentials_error
    return user

def require_manager(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.gestionnaire:
        raise HTTPException(status_code=403,detail="Insufficient permissions")
    return user