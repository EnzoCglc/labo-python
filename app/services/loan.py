from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Loan, Equipement
from app.schemas import LoanCreate

class EquipementNotFound(Exception):
    """This equipment does not exist."""


class EquipementAlreadyLoaned(Exception):
    """This equipment is already loaned."""

def create_loan(db: Session, data: LoanCreate, user_id: int) -> Loan:
    
    if db.get(Equipement, data.equipment_id) is None:
        raise EquipementNotFound(data.equipment_id)
    
    loan = Loan(user_id=user_id, **data.model_dump())
    db.add(loan)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EquipementAlreadyLoaned(data.equipment_id)
    db.refresh(loan)
    return loan