from sqlalchemy import select

from app import models
from app.core.database import Base, SessionLocal, engine
from app.models import Equipement, Role, User
from app.core.security import hash_password

USERS = [
    ("gestionnaire", "gestion123", Role.gestionnaire),
    ("etudiant", "abc123", Role.etudiant),
    ("etudiant2", "abc1234", Role.etudiant),
]

EQUIPEMENTS = [
    ("PC-001", "Ordinateur fixe Lenovo", "ordinateur")
]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for username, password, role in USERS:
            if not db.scalar(select(User).where(User.username == username)):
                db.add(User(username=username, hashed_password=hash_password(password), role=role))
        for reference , nom, categorie in EQUIPEMENTS:
            if not db.scalar(select(Equipement).where(Equipement.reference == reference)):
                db.add(Equipement(reference=reference, nom=nom, categorie=categorie))

        db.commit()
    finally:
        db.close()
                    
seed()
print("Données injecter dans la db")