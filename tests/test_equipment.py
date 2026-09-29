from sqlalchemy import func, select

from app.models import Equipement


def test_duplicate_reference_is_rejected(client, db, manager_headers):
    payload = {"reference": "OSC-001", "nom": "Oscilloscope", "categorie": "mesure"}

    first = client.post("/equipment", json=payload, headers=manager_headers)
    assert first.status_code == 201

    second = client.post("/equipment", json=payload, headers=manager_headers)
    assert second.status_code == 409

    count = db.scalar(select(func.count()).select_from(Equipement).where(Equipement.reference == "OSC-001"))
    assert count == 1
