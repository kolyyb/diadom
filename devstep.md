# Plan de Développement - Di@dom Inventory Manager

## Objectif
Créer une application web de gestion d'inventaire pour Di@dom, permettant de suivre les stocks de matériel médical dans différents emplacements.

## Technologies
- Backend: Python avec Flask
- Base de données: SQLite avec SQLAlchemy
- Frontend: HTML, CSS (Bootstrap 5), JavaScript
- Tests: pytest

## Étapes de Développement

### 1. Configuration initiale

1. Créer un environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
```

2. Installer les dépendances :
```bash
pip install flask flask-sqlalchemy flask-migrate python-docx
```

3. Structure du projet :
```
ia/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── base.html
│       └── index.html
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
├── .env
├── .gitignore
├── config.py
└── requirements.txt
```

### 2. Configuration de la base de données

1. Dans `config.py` :
```python
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

2. Dans `.env` :
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
```

### 3. Modèles de données

Dans `app/models.py` :
- Classe `Product` pour gérer les produits médicaux
- Classe `ProductHistory` pour suivre les modifications
- Liste `AVAILABLE_PRODUCTS` pour les produits disponibles
- Mapping `PRODUCT_NAME_MAPPING` pour la reconnaissance des noms

### 4. Routes et API

Dans `app/routes.py` :
- `/` : Page d'accueil avec tableau des produits
- `/api/products` : CRUD des produits
- `/api/reset-inventory` : Remise à zéro des stocks
- `/api/export-csv` : Export en CSV
- `/api/generate-order` : Génération de bon de commande

### 5. Interface utilisateur

Dans `app/templates/` :
1. `base.html` : Template de base avec Bootstrap
2. `index.html` : 
   - Tableau des produits avec totaux
   - Formulaire d'ajout/modification
   - Boutons d'action (export, commande)

### 6. Tests

Dans `tests/` :
1. `test_models.py` : Tests des modèles
2. `test_routes.py` : Tests des routes et API

### 7. Initialisation de la base de données

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 8. Lancement de l'application

```bash
flask run --port=5001
```

### 9. Fonctionnalités principales

1. Gestion des produits :
   - Ajout, modification, suppression
   - Deux emplacements : box et appartement
   - Historique des modifications

2. Calculs et totaux :
   - Somme par produit
   - Totaux par emplacement

3. Export et documents :
   - Export CSV des stocks
   - Génération de bons de commande

4. Interface utilisateur :
   - Design responsive avec Bootstrap
   - Tableau récapitulatif
   - Actions rapides

### 10. Maintenance

1. Tests :
```bash
python -m pytest
```

2. Base de données :
```bash
# Réinitialisation si nécessaire
rm -f app.db
flask db upgrade
```

### 11. Sécurité

- Validation des entrées côté serveur
- Protection CSRF avec Flask-WTF
- Sanitization des données

### 12. Bonnes pratiques

1. Code :
   - Documentation des fonctions
   - Tests unitaires
   - Gestion des erreurs

2. Base de données :
   - Migrations versionnées
   - Transactions sécurisées
   - Historique des modifications

3. Interface :
   - Design responsive
   - Messages d'erreur clairs
   - Confirmations des actions importantes

## Fonctionnalités Principales

### Gestion des Produits 
- Ajout de nouveaux produits
- Modification des quantités et emplacements
- Suppression de produits
- Liste prédéfinie de produits médicaux

### Gestion des Emplacements 
- Deux emplacements possibles : box et apartment
- Validation des emplacements
- Filtrage par emplacement
- Totaux par emplacement

### Suivi des Modifications 
- Historique complet des modifications
- Date et heure de chaque action
- Détails des changements (anciennes et nouvelles valeurs)
- Page dédiée à l'historique

### Export des Données 
- Export de l'inventaire en CSV
- Nom de fichier avec date et heure
- Inclusion de toutes les informations importantes

### Statistiques et Totaux 
- Nombre de produits par emplacement
- Quantités totales par emplacement
- Mise à jour en temps réel des totaux

## Sécurité et Validation
- Validation des données côté serveur
- Protection contre les entrées invalides
- Confirmation des actions importantes
- Gestion des erreurs

## Interface Utilisateur
- Design moderne avec Bootstrap 5
- Interface responsive
- Navigation intuitive
- Feedback visuel des actions
- Filtres et recherche faciles d'utilisation
