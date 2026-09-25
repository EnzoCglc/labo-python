from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Equipement
from app.schemas import EquipementCreate


class ReferenceAlreadyExists(Exception):
    """La référence d'équipement est déjà utilisée."""


def list_equipements(db: Session) -> list[Equipement]:
    return list(db.scalars(select(Equipement).order_by(Equipement.id)))


def create_equipement(db: Session, data: EquipementCreate) -> Equipement:
    equipement = Equipement(**data.model_dump())
    db.add(equipement)
    try:
        db.commit()
    except IntegrityError:          
        db.rollback()
        raise ReferenceAlreadyExists(data.reference)
    db.refresh(equipement)          
    return equipement