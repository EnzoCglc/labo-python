from sqlalchemy import select

from app.models import Loan


def active_loans(session_factory, equipment_id: int) -> list[Loan]:
    # Fresh session so we read what is really committed in the database
    with session_factory() as session:
        return list(session.scalars(
            select(Loan).where(Loan.equipment_id == equipment_id, Loan.date_retour.is_(None))
        ))


def all_loans(session_factory) -> list[Loan]:
    with session_factory() as session:
        return list(session.scalars(select(Loan)))


def get_loan(session_factory, loan_id: int) -> Loan:
    with session_factory() as session:
        return session.get(Loan, loan_id)


def borrow(client, headers, equipment_id: int):
    return client.post("/loans", json={"equipment_id": equipment_id}, headers=headers)


def test_first_loan_is_created(client, session_factory, users, equipment, student_headers):
    response = borrow(client, student_headers, equipment.id)

    assert response.status_code == 201
    body = response.json()
    assert body["date_retour"] is None
    assert body["user_id"] == users["etudiant"].id

    loans = active_loans(session_factory, equipment.id)
    assert len(loans) == 1
    assert loans[0].id == body["id"]
    assert loans[0].date_retour is None


def test_second_loan_of_same_equipment_is_rejected(client, session_factory, users, equipment, student_headers, student2_headers):
    assert borrow(client, student_headers, equipment.id).status_code == 201

    response = borrow(client, student2_headers, equipment.id)

    assert response.status_code == 409
    loans = active_loans(session_factory, equipment.id)
    assert len(loans) == 1
    assert loans[0].user_id == users["etudiant"].id


def test_return_by_another_student_is_forbidden(client, session_factory, equipment, student_headers, student2_headers):
    loan_id = borrow(client, student_headers, equipment.id).json()["id"]

    response = client.patch(f"/loans/{loan_id}/return", headers=student2_headers)

    assert response.status_code == 403
    assert get_loan(session_factory, loan_id).date_retour is None


def test_authorized_return_frees_equipment(client, session_factory, equipment, student_headers, student2_headers):
    loan_id = borrow(client, student_headers, equipment.id).json()["id"]

    response = client.patch(f"/loans/{loan_id}/return", headers=student_headers)

    assert response.status_code == 200
    assert response.json()["date_retour"] is not None
    assert get_loan(session_factory, loan_id).date_retour is not None

    new_loan = borrow(client, student2_headers, equipment.id)
    assert new_loan.status_code == 201


def test_replayed_old_return_does_not_close_new_loan(client, session_factory, equipment, student_headers, student2_headers):
    old_loan_id = borrow(client, student_headers, equipment.id).json()["id"]
    assert client.patch(f"/loans/{old_loan_id}/return", headers=student_headers).status_code == 200
    new_loan_id = borrow(client, student2_headers, equipment.id).json()["id"]

    response = client.patch(f"/loans/{old_loan_id}/return", headers=student_headers)

    assert response.status_code == 409
    assert get_loan(session_factory, new_loan_id).date_retour is None


def test_manager_sees_full_history(client, users, equipment, manager_headers, student_headers, student2_headers):
    first_id = borrow(client, student_headers, equipment.id).json()["id"]
    client.patch(f"/loans/{first_id}/return", headers=student_headers)
    second_id = borrow(client, student2_headers, equipment.id).json()["id"]

    response = client.get(f"/equipment/{equipment.id}/history", headers=manager_headers)

    assert response.status_code == 200
    history = response.json()
    assert [item["loan_id"] for item in history] == [second_id, first_id]
    assert history[0]["username"] == "etudiant2"
    assert history[1]["username"] == "etudiant"
    assert history[0]["user_id"] == users["etudiant2"].id
    assert history[1]["user_id"] == users["etudiant"].id
    assert history[0]["date_emprunt"] >= history[1]["date_emprunt"]
    assert history[0]["date_retour"] is None
    assert history[1]["date_retour"] is not None


def test_student_cannot_see_history(client, equipment, student_headers):
    borrow(client, student_headers, equipment.id)

    response = client.get(f"/equipment/{equipment.id}/history", headers=student_headers)

    assert response.status_code == 403


def test_loan_without_token_is_rejected(client, session_factory, equipment):
    response = client.post("/loans", json={"equipment_id": equipment.id})

    assert response.status_code == 401
    assert all_loans(session_factory) == []


def test_loan_on_unknown_equipment_returns_404(client, session_factory, users, student_headers):
    response = borrow(client, student_headers, 9999)

    assert response.status_code == 404
    assert all_loans(session_factory) == []
