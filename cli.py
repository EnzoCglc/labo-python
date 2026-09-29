import argparse
import csv
import json
import sys

from app.core.database import SessionLocal
from app.services.equipement import list_equipements

def main():
    parser = argparse.ArgumentParser(description="Mon outil de gestion d'inventaire")
    parser.add_argument("commande", type=str, help="La commande à exécuter (ex: inventaire)")
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="text",
        choices=["text", "json", "csv"],
        help="Le format de sortie des données"
    )

    args = parser.parse_args()

    if args.commande == "inventaire":
        db = SessionLocal()
        try:
            inventaire = [
                {
                    "reference": equipement.reference,
                    "nom": equipement.nom,
                    "disponible": equipement.is_available,
                }
                for equipement in list_equipements(db)
            ]
        finally:
            db.close()

        if args.format == "json":
            print(json.dumps(inventaire, indent=2, ensure_ascii=False))
        elif args.format == "csv":
            writer = csv.DictWriter(sys.stdout, fieldnames=["reference", "nom", "disponible"])
            writer.writeheader()
            writer.writerows(inventaire)
        else:
            for item in inventaire:
                statut = "disponible" if item["disponible"] else "emprunté"
                print(f"{item['reference']} - {item['nom']} : {statut}")

    else:
        print(f"Commande '{args.commande}' inconnue. Utilisez 'inventaire'.")


if __name__ == "__main__":
    main()
