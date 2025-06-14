# Application de Gestion d'Inventaire Médical

Application web Python permettant de gérer l'inventaire de matériel médical avec deux emplacements de stockage (box et appartement).

## Fonctionnalités

- Gestion CRUD des produits (ajout, modification, suppression)
- Deux emplacements de stockage : box et appartement
- Calcul des sommes et totaux des produits
- Génération automatique de bons de commande
- Export des données en CSV
- Historique des modifications
- Remise à zéro des stocks

## Installation

1. Cloner le dépôt :
```bash
git clone <repository_url>
cd ia
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
flask db upgrade
```

## Configuration

1. Copier le fichier de bon de commande dans le dossier `templates` :
```bash
cp "BON COMMANDE PATIENT_KP100225.docx" templates/
```

2. Créer le dossier pour les fichiers générés :
```bash
mkdir generated_files
```

## Utilisation

1. Lancer l'application :
```bash
flask run
```

2. Accéder à l'application dans votre navigateur : http://localhost:5000

### Gestion des Produits

- **Ajouter un produit** : Utilisez le formulaire "Ajouter un Produit"
- **Modifier un produit** : Cliquez sur l'icône de modification dans la liste des produits
- **Supprimer un produit** : Cliquez sur l'icône de suppression dans la liste des produits

### Génération de Documents

- **Export CSV** : Cliquez sur le bouton "Exporter CSV" pour télécharger l'inventaire complet
- **Bon de Commande** : Cliquez sur le bouton "Bon de Commande" pour générer un bon de commande pré-rempli

### Historique

- Consultez l'historique des modifications en cliquant sur le bouton "Historique"

## Tests

Pour exécuter les tests :
```bash
python -m pytest
```

## Structure du Projet

```
ia/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── history.html
├── migrations/
├── templates/
│   └── BON COMMANDE PATIENT_KP100225.docx
├── tests/
│   ├── test_models.py
│   └── test_routes.py
├── generated_files/
├── config.py
└── requirements.txt
```
## TODO
utilisation d'une constante pour definir le fichier bondecommande
Supprimer la fonctionalité "ajout de nouveaux produits" qui est inutile finalement
Ajouter la fonctionalité "envoyer le bon de commande généré par mail" à la pharmacienne
Adapter l'app dans une version mobile
Rajouter la fonctionalité "Calendrier des livraisons"
