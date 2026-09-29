import json
import sys

import cli


def run_inventory(monkeypatch, capsys) -> list[dict]:
    monkeypatch.setattr(sys, "argv", ["cli.py", "inventaire", "--format", "json"])
    cli.main()
    output = capsys.readouterr().out
    return json.loads(output)  # fails if the output is not valid JSON


def availability(inventory: list[dict], reference: str) -> bool:
    return next(item["disponible"] for item in inventory if item["reference"] == reference)


def test_cli_inventory_reflects_loans(monkeypatch, capsys, client, equipment, student_headers):
    loan = client.post("/loans", json={"equipment_id": equipment.id}, headers=student_headers)
    assert loan.status_code == 201

    inventory = run_inventory(monkeypatch, capsys)
    assert availability(inventory, equipment.reference) is False

    returned = client.patch(f"/loans/{loan.json()['id']}/return", headers=student_headers)
    assert returned.status_code == 200

    inventory = run_inventory(monkeypatch, capsys)
    assert availability(inventory, equipment.reference) is True
