from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Loan, Equipement, Role, User, utcnow
from app.schemas import LoanCreate

class EquipementNotFound(Exception):
    """This equipment does not exist."""


class EquipementAlreadyLoaned(Exception):
    """This equipment is already loaned."""

class LoanNotFound(Exception):
    """This loan does not exist."""

class NotLoanOwner(Exception):
    """This loan belongs to another user."""

class LoanAlreadyReturned(Exception):
    """This loan has already been returned."""

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

def return_loan(db:Session, loan_id: int, user: User):
    
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    
    if user.role != Role.gestionnaire and loan.user_id != user.id:
        raise NotLoanOwner(loan_id)
    
    if loan.date_retour is not None:
        raise LoanAlreadyReturned(loan_id)
    
    loan.date_retour = utcnow()
    db.commit()
    db.refresh(loan)
    return loan

def list_loans(db: Session, user: User) -> list[Loan]:
    query = select(Loan).order_by(Loan.date_emprunt.desc())
    if user.role != Role.gestionnaire:
        query = query.where(Loan.user_id == user.id)
    return list(db.scalars(query))