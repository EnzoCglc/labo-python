# Prêts de matériel du laboratoire

API REST de gestion des prêts de matériel d'un laboratoire, développée avec **FastAPI** et **SQLAlchemy**. Les utilisateurs s'authentifient par JWT ; les étudiants empruntent et rendent du matériel, les gestionnaires supervisent l'ensemble des prêts et consultent l'historique de chaque équipement.

Un outil en ligne de commande permet aussi d'exporter l'inventaire (texte, JSON ou CSV).

## Fonctionnalités

- Authentification OAuth2 (mot de passe → token JWT), mots de passe hachés avec bcrypt
- Deux rôles : `etudiant` et `gestionnaire`
- Création et liste des équipements (référence unique)
- Emprunt et retour de matériel, avec **un seul prêt actif par équipement** garanti en base (index unique partiel)
- Historique des prêts d'un équipement (gestionnaire uniquement)
- CLI d'inventaire avec statut de disponibilité

## Stack

| Élément          | Outil                    |
|------------------|--------------------------|
| Langage          | Python 3.13              |
| Framework web    | FastAPI + Uvicorn        |
| ORM / BDD        | SQLAlchemy 2.0 / SQLite  |
| Validation       | Pydantic v2              |
| Auth             | PyJWT + bcrypt           |
| Tests            | pytest + TestClient      |

## Structure du projet

```
.
├── app/
│   ├── main.py              # Création de l'app FastAPI et des tables
│   ├── routes.py            # Définition des endpoints
│   ├── models.py            # Modèles SQLAlchemy (User, Equipement, Loan)
│   ├── schemas.py           # Schémas Pydantic (entrées / sorties)
│   ├── core/
│   │   ├── database.py      # Engine, session, get_db
│   │   ├── security.py      # Hachage des mots de passe, création des JWT
│   │   └── dependencies.py  # get_current_user, require_manager
│   └── services/            # Logique métier (auth, equipement, loan)
├── tests/                   # Tests pytest (API + CLI) sur base en mémoire
├── cli.py                   # Outil en ligne de commande
├── seed.py                  # Données de démonstration
├── requirements.txt
└── .env.example
```

## Installation

```bash
git clone <url-du-depot>
cd labo-python

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Copier le fichier d'exemple puis renseigner une clé secrète :

```bash
cp .env.example .env
```

| Variable                      | Description                         | Exemple                   |
|-------------------------------|-------------------------------------|---------------------------|
| `DATABASE_URL`                | URL de connexion SQLAlchemy         | `sqlite:///./labo.db`     |
| `SECRET_KEY`                  | Clé de signature des tokens JWT     | chaîne aléatoire longue   |
| `ALGORITHM`                   | Algorithme de signature JWT         | `HS256`                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité d'un token (min)  | `30`                      |

Pour générer une clé secrète :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Données de démonstration

```bash
python seed.py
```

Comptes créés :

| Utilisateur    | Mot de passe | Rôle         |
|----------------|--------------|--------------|
| `gestionnaire` | `gestion123` | gestionnaire |
| `etudiant`     | `abc123`     | etudiant     |
| `etudiant2`    | `abc1234`    | etudiant     |

Équipements créés :

| Référence  | Nom                           | Catégorie            |
|------------|-------------------------------|----------------------|
| `PC-001`   | Ordinateur fixe Lenovo        | ordinateur           |
| `PC-002`   | Ordinateur fixe HP EliteDesk  | ordinateur           |
| `PC-003`   | Portable Dell Latitude 5540   | ordinateur           |
| `PC-004`   | Portable MacBook Pro 14       | ordinateur           |
| `ECR-001`  | Écran Dell 24 pouces          | ecran                |
| `ECR-002`  | Écran LG 27 pouces 4K         | ecran                |
| `CLV-001`  | Clavier Logitech K120         | peripherique         |
| `SOU-001`  | Souris Logitech M185          | peripherique         |
| `CAM-001`  | Webcam Logitech C920          | peripherique         |
| `RPI-001`  | Raspberry Pi 5                | carte-electronique   |
| `ARD-001`  | Arduino Uno R4                | carte-electronique   |
| `VID-001`  | Vidéoprojecteur Epson EB-W49  | audiovisuel          |
| `HDMI-001` | Câble HDMI 2 m                | cable                |

Le script est idempotent : il peut être relancé sans créer de doublons.

## Lancer l'API

```bash
uvicorn app.main:app --reload
```

- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs

Dans Swagger, le bouton **Authorize** permet de se connecter avec l'un des comptes ci-dessus.

## Endpoints

| Méthode | Route                              | Accès         | Description                                              |
|---------|------------------------------------|---------------|----------------------------------------------------------|
| GET     | `/health`                          | Public        | Vérifie que l'API répond                                 |
| POST    | `/token`                           | Public        | Connexion (form `username` / `password`) → token JWT     |
| GET     | `/me`                              | Authentifié   | Infos de l'utilisateur connecté                          |
| GET     | `/equipment`                       | Authentifié   | Liste des équipements                                    |
| POST    | `/equipment`                       | Authentifié   | Crée un équipement                                       |
| GET     | `/equipment/{id}/history`          | Gestionnaire  | Historique des prêts d'un équipement                     |
| POST    | `/loans`                           | Authentifié   | Emprunte un équipement                                   |
| PATCH   | `/loans/{id}/return`               | Authentifié   | Rend un prêt (le sien, ou n'importe lequel si gestionnaire) |
| GET     | `/loans`                           | Authentifié   | Ses propres prêts (tous les prêts si gestionnaire)       |

### Codes d'erreur

| Code | Cas                                                                  |
|------|----------------------------------------------------------------------|
| 401  | Identifiants incorrects, token absent, invalide ou expiré            |
| 403  | Rôle insuffisant, ou retour d'un prêt appartenant à un autre étudiant |
| 404  | Équipement ou prêt inexistant                                        |
| 409  | Référence déjà utilisée, équipement déjà emprunté, prêt déjà rendu   |
| 422  | Données invalides (validation Pydantic)                              |

### Exemple avec curl

```bash
# 1. Récupérer un token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
  -d "username=etudiant&password=abc123" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Emprunter l'équipement n°1
curl -X POST http://127.0.0.1:8000/loans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"equipment_id": 1}'

# 3. Rendre le prêt n°1
curl -X PATCH http://127.0.0.1:8000/loans/1/return \
  -H "Authorization: Bearer $TOKEN"
```

### Création d'un équipement

```json
{
  "reference": "PC-005",
  "nom": "Portable Lenovo ThinkPad T14",
  "categorie": "ordinateur"
}
```

La référence n'accepte que lettres, chiffres, `-` et `_` (50 caractères max).

## CLI d'inventaire

```bash
python cli.py inventaire              # format texte (par défaut)
python cli.py inventaire -f json
python cli.py inventaire -f csv > inventaire.csv
```

Exemple de sortie texte :

```
PC-001 - Ordinateur fixe Lenovo : emprunté
PC-002 - Ordinateur fixe HP EliteDesk : disponible
PC-003 - Portable Dell Latitude 5540 : disponible
...
```

## Tests

```bash
pytest
```

Les tests utilisent une base SQLite **en mémoire**, recréée pour chaque test : la base `labo.db` n'est jamais modifiée. Ils couvrent les équipements, les prêts (droits, conflits, retours) et la CLI. Un fichier `.env` avec `SECRET_KEY`, `ALGORITHM` et `ACCESS_TOKEN_EXPIRE_MINUTES` doit être présent.
