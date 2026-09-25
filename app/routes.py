from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_manager
from app.models import User
from app.schemas import EquipementCreate, EquipementOut
from app.services import equipement as equipement_service

router = APIRouter()

@router.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

@router.get("/equipment", status_code=200, tags=["equipements"], dependencies=[Depends(get_current_user)])
def get_equipment(db: Session = Depends(get_db)):
    return equipement_service.list_equipements(db)

@router.post("/equipment", status_code=201, tags=["equipements"], dependencies=[Depends(get_current_user)])
def post_equipment(payload: EquipementCreate, db: Session = Depends(get_db)):
    try:
        return equipement_service.create_equipement(db, payload)
    except equipement_service.ReferenceAlreadyExists:
        raise HTTPException(status_code=409, detail="This equipment reference already exists.",)