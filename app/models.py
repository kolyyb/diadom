from datetime import datetime
from sqlalchemy.orm import validates
from app import db

# Liste des produits disponibles
AVAILABLE_PRODUCTS = [
    'Lignes à sang',
    'K7 Ergo Flow',
    'K7 FLOW',
    'Dialyseurs',
    'Dialysats',
    'Sodium',
    'Chlorexydine',
    'Aiguilles à fistules',
    'Rallonges aiguilles',
    'Kits de ponctions',
    'Tuyau extentions',
    'Raccords Y',
    'Seringues 20 ml',
    'Enoxaparine',
    'Seringues 10 ml'
]

# Mapping entre les noms dans le bon de commande et les noms dans la base de données
PRODUCT_NAME_MAPPING = {
    'Lignes à sang': ['PHYSIDIA LIGNES A SANG A-V PHYSILINE (1/RA)'],
    'K7 Ergo Flow': ['PHYSIDIA CASSETTE dialysat PHYSI.FLOW. ERGO (1 pour 2 RA soit 3/semaine)'],
    'K7 FLOW': ['PHYSIDIA CASSETTE dialysat PHYSI.FLOW : avoir toujours 5 unités en stock'],
    'Dialyseurs': ['DIALYSEUR FX60 (1/RA)'],
    'Dialysats': ['PHYSIDIA DIALYSAT K1 5L/poche (5 poches/RA)'],
    'Sodium': ['SODIUM CHL.0.9% emoluer 2 litres (1/RA)'],
    'Aiguilles à fistules': ['AIG.PLUME V16G-R20-R (Fresenius) (2/RA)'],
    'Rallonges aiguilles': ['RACCORD FISTULE LG200 (Hémodia) ( 2/RA)'],
    'Kits de ponctions': ['SET DIALYSE FISTULE medium 7/8 (1/RA)'],
    'Tuyau extentions': ['PHYSIDIA LIGNE EXTENSION 3m (2/RA)'],
    'Raccords Y': ['RACCORD Y pour UNIPONCTURE (1/RA)'],
    'Seringues 20 ml': ['SERINGUE 20ML', 'SERINGUE 20', 'SERINGUES 20'],
    'Enoxaparine': ['ENOXAPARINE 2 000 UI/0,2 ml seringue (1/RA)'],
    'Seringues 10 ml': ['SERINGUE 10ML', 'SERINGUE 10', 'SERINGUES 10']
}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String(50), nullable=False)  # 'box' ou 'apartment'
    description = db.Column(db.Text)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    history = db.relationship('ProductHistory', backref='product', lazy=True, cascade='all, delete-orphan')

    VALID_LOCATIONS = ['box', 'apartment']

    def __repr__(self):
        return f'<Product {self.name}>'

    @validates('location')
    def validate_location(self, key, location):
        if location not in self.VALID_LOCATIONS:
            raise ValueError(f"Location must be one of: {', '.join(self.VALID_LOCATIONS)}")
        return location

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'location': self.location,
            'description': self.description,
            'last_modified': self.last_modified.isoformat()
        }

    def log_change(self, action, old_values=None):
        """Log un changement dans l'historique du produit.
        
        Args:
            action (str): Type d'action ('create', 'update', 'delete', 'reset')
            old_values (dict): Anciennes valeurs avant modification
        """
        if old_values is None:
            old_values = {}
        
        # Si c'est une mise à jour et qu'il n'y a pas de changement, ne pas créer d'historique
        if action == 'update':
            if (old_values.get('quantity') == self.quantity and 
                old_values.get('location') == self.location):
                return
        
        history = ProductHistory(
            product=self,
            action=action,
            old_quantity=old_values.get('quantity'),
            new_quantity=self.quantity,
            old_location=old_values.get('location'),
            new_location=self.location
        )
        db.session.add(history)

    @classmethod
    def initialize_products(cls):
        """Initialise tous les produits disponibles avec une quantité de 0 s'ils n'existent pas déjà"""
        for product_name in AVAILABLE_PRODUCTS:
            # Vérifie si le produit existe déjà dans le box
            if not cls.query.filter_by(name=product_name, location='box').first():
                product = cls(name=product_name, quantity=0, location='box')
                db.session.add(product)
                db.session.flush()  # Pour obtenir l'ID du produit
                product.log_change('create')

            # Vérifie si le produit existe déjà dans l'appartement
            if not cls.query.filter_by(name=product_name, location='apartment').first():
                product = cls(name=product_name, quantity=0, location='apartment')
                db.session.add(product)
                db.session.flush()  # Pour obtenir l'ID du produit
                product.log_change('create')
        
        db.session.commit()

class ProductHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, reset
    old_quantity = db.Column(db.Integer)
    new_quantity = db.Column(db.Integer)
    old_location = db.Column(db.String(50))
    new_location = db.Column(db.String(50))

    def __repr__(self):
        return f'<ProductHistory {self.product_id} {self.action}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'old_quantity': self.old_quantity,
            'new_quantity': self.new_quantity,
            'old_location': self.old_location,
            'new_location': self.new_location
        }
