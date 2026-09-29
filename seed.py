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
    ("PC-001", "Ordinateur fixe Lenovo", "ordinateur"),
    ("PC-002", "Ordinateur fixe HP EliteDesk", "ordinateur"),
    ("PC-003", "Portable Dell Latitude 5540", "ordinateur"),
    ("PC-004", "Portable MacBook Pro 14", "ordinateur"),
    ("ECR-001", "Écran Dell 24 pouces", "ecran"),
    ("ECR-002", "Écran LG 27 pouces 4K", "ecran"),
    ("CLV-001", "Clavier Logitech K120", "peripherique"),
    ("SOU-001", "Souris Logitech M185", "peripherique"),
    ("CAM-001", "Webcam Logitech C920", "peripherique"),
    ("RPI-001", "Raspberry Pi 5", "carte-electronique"),
    ("ARD-001", "Arduino Uno R4", "carte-electronique"),
    ("VID-001", "Vidéoprojecteur Epson EB-W49", "audiovisuel"),
    ("HDMI-001", "Câble HDMI 2 m", "cable"),
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