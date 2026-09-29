from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Equipement, Loan
from app.schemas import EquipementCreate, HistoryItem


class ReferenceAlreadyExists(Exception):
    """La référence d'équipement est déjà utilisée."""

class EquipementNotFound(Exception):
    """This equipment does not exist."""


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


def get_equipement_history(db: Session, equipment_id: int) -> list[HistoryItem]:
    if db.get(Equipement, equipment_id) is None:
        raise EquipementNotFound(equipment_id)

    # joinedload charge l'emprunteur dans la même requête (évite N+1)
    query = (
        select(Loan)
        .options(joinedload(Loan.user))
        .where(Loan.equipment_id == equipment_id)
        .order_by(Loan.date_emprunt.desc(), Loan.id.desc())
    )
    return [
        HistoryItem(
            loan_id=loan.id,
            user_id=loan.user_id,
            username=loan.user.username,
            date_emprunt=loan.date_emprunt,
            date_retour=loan.date_retour,
        )
        for loan in db.scalars(query)
    ]