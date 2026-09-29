from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.models import User
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_manager
from app.schemas import EquipementCreate, LoanCreate
from app.services import equipement
from app.services import loan
from app.services import auth as auth_service

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

@router.get("/equipment", status_code=200, response_model=list[schemas.EquipementOut], tags=["equipements"], dependencies=[Depends(get_current_user)])
def get_equipment(db: Session = Depends(get_db)):
    return equipement.list_equipements(db)

@router.post("/equipment", status_code=201, response_model=schemas.EquipementOut, tags=["equipements"], dependencies=[Depends(get_current_user)])
def post_equipment(payload: EquipementCreate, db: Session = Depends(get_db)):
    try:
        return equipement.create_equipement(db, payload)
    except equipement.ReferenceAlreadyExists:
        raise HTTPException(status_code=409, detail="This equipment reference already exists.",)

@router.get("/equipment/{equipment_id}/history", status_code=200, response_model=list[schemas.HistoryItem], tags=["equipements"], dependencies=[Depends(require_manager)])
def get_equipment_history(equipment_id: int, db: Session = Depends(get_db)):
    try:
        return equipement.get_equipement_history(db, equipment_id)
    except equipement.EquipementNotFound:
        raise HTTPException(status_code=404, detail="Equipment not found.")

@router.post("/loans", status_code=201, response_model=schemas.LoanOut, tags=["loans"])
def post_loan(payload: LoanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return loan.create_loan(db, payload, current_user.id)
    except loan.EquipementNotFound:
        raise HTTPException(status_code=404, detail="Equipment not found.")
    except loan.EquipementAlreadyLoaned:
        raise HTTPException(status_code=409, detail="This equipment is already loaned.")
  
@router.patch("/loans/{loan_id}/return", response_model=schemas.LoanOut, tags=["loans"])
def return_loan(loan_id: int , db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return loan.return_loan(db, loan_id, current_user)
    except loan.LoanNotFound:
         raise HTTPException(status_code=404, detail="Loan not found.")
    except loan.NotLoanOwner:
        raise HTTPException(status_code=403, detail="You can only return your own loans.")
    except loan.LoanAlreadyReturned:
        raise HTTPException(status_code=409, detail="This loan has already been returned.")

@router.get("/loans", status_code=200, response_model=list[schemas.LoanOut], tags=["loans"])
def get_loans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return loan.list_loans(db, current_user)