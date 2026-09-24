import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, enum.Enum):
    etudiant = "etudiant"
    gestionnaire = "gestionnaire"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.etudiant)

    loans: Mapped[list["Loan"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"


class Equipement(Base):
    __tablename__ = "equipements"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(50))
    categorie: Mapped[str] = mapped_column(String(50))

    # Historique trié du plus récent au plus ancien
    loans: Mapped[list["Loan"]] = relationship(
        back_populates="equipment",
        order_by="Loan.date_emprunt.desc()",
    )

    def __repr__(self) -> str:
        return f"<Equipement {self.nom} ({self.reference})>"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipements.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date_emprunt: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # NULL tant que le prêt est actif
    date_retour: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    equipment: Mapped["Equipement"] = relationship(back_populates="loans")
    user: Mapped["User"] = relationship(back_populates="loans")

    __table_args__ = (
        # Un seul prêt actif (date_retour IS NULL) par matériel
        Index(
            "uq_one_active_loan_per_equipment",
            "equipment_id",
            unique=True,
            sqlite_where=text("date_retour IS NULL"),
            postgresql_where=text("date_retour IS NULL"),
        ),
    )

    def __repr__(self) -> str:
        return f"<Loan {self.id} - Equipement {self.equipment_id} emprunté par User {self.user_id}>"