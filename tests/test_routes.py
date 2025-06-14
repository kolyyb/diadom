import pytest
from app import create_app, db
from app.models import Product, ProductHistory, AVAILABLE_PRODUCTS
import json
from datetime import datetime
import os

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_index_page(client, init_database):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Inventaire'.encode() in response.data
    # Vérifier la présence du tableau récapitulatif
    assert 'Totaux par Produit'.encode() in response.data
    # Vérifier la présence des boutons d'action
    assert 'Exporter CSV'.encode() in response.data
    assert 'Bon de Commande'.encode() in response.data

def test_add_product(client, init_database):
    response = client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 10,
        'location': 'box'
    })
    assert response.status_code == 302  # Redirection

    # Vérifier que le produit a été ajouté
    with client.application.app_context():
        product = Product.query.filter_by(name='Lignes à sang').first()
        assert product is not None
        assert product.quantity == 10
        assert product.location == 'box'

        # Vérifier l'historique
        history = ProductHistory.query.filter_by(product_id=product.id).first()
        assert history is not None
        assert history.action == 'create'
        assert history.new_quantity == 10

def test_update_product(client, init_database):
    # Créer un produit
    with client.application.app_context():
        product = Product(name='K7 FLOW', quantity=5, location='box')
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    # Mettre à jour le produit
    response = client.put(f'/api/products/{product_id}', 
                         data=json.dumps({'quantity': 15, 'location': 'apartment'}),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['product']['quantity'] == 15
    assert data['product']['location'] == 'apartment'

    # Vérifier la mise à jour en base
    with client.application.app_context():
        updated_product = Product.query.get(product_id)
        assert updated_product.quantity == 15
        assert updated_product.location == 'apartment'

        # Vérifier l'historique
        history = ProductHistory.query.filter_by(
            product_id=product_id,
            action='update'
        ).first()
        assert history is not None
        assert history.old_quantity == 5
        assert history.new_quantity == 15
        assert history.old_location == 'box'
        assert history.new_location == 'apartment'

def test_delete_product(client, init_database):
    # Créer un produit
    with client.application.app_context():
        product = Product(name='Dialyseurs', quantity=3, location='box')
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    # Supprimer le produit
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 204

    # Vérifier que le produit a été supprimé
    with client.application.app_context():
        deleted_product = Product.query.get(product_id)
        assert deleted_product is None

        # Vérifier l'historique
        history = ProductHistory.query.filter_by(
            product_id=product_id,
            action='delete'
        ).first()
        assert history is not None

def test_reset_inventory(client, init_database):
    # Créer quelques produits
    with client.application.app_context():
        products = [
            Product(name='Lignes à sang', quantity=10, location='box'),
            Product(name='K7 FLOW', quantity=5, location='apartment')
        ]
        for p in products:
            db.session.add(p)
        db.session.commit()

    # Réinitialiser l'inventaire
    response = client.post('/api/reset-inventory')
    assert response.status_code == 302  # Redirection

    # Vérifier que tous les produits sont à 0
    with client.application.app_context():
        products = Product.query.all()
        for p in products:
            assert p.quantity == 0

        # Vérifier l'historique
        history = ProductHistory.query.filter_by(action='reset').all()
        assert len(history) == 2

def test_initialize_products(client, init_database):
    response = client.get('/')  # L'initialisation se fait lors de l'accès à la page d'accueil
    assert response.status_code == 200

    with client.application.app_context():
        # Vérifier que tous les produits ont été créés
        for product_name in AVAILABLE_PRODUCTS:
            # Vérifier dans le box
            box_product = Product.query.filter_by(
                name=product_name,
                location='box'
            ).first()
            assert box_product is not None
            assert box_product.quantity == 0

            # Vérifier dans l'appartement
            apt_product = Product.query.filter_by(
                name=product_name,
                location='apartment'
            ).first()
            assert apt_product is not None
            assert apt_product.quantity == 0

def test_product_totals(client, init_database):
    # Créer quelques produits avec des quantités connues
    with client.application.app_context():
        products = [
            Product(name='Lignes à sang', quantity=10, location='box'),
            Product(name='Lignes à sang', quantity=5, location='apartment'),
            Product(name='K7 FLOW', quantity=3, location='box'),
            Product(name='K7 FLOW', quantity=2, location='apartment')
        ]
        for p in products:
            db.session.add(p)
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    
    # Vérifier que les totaux sont affichés
    assert 'Lignes à sang'.encode() in response.data  # UTF-8 encoded
    assert 'K7 FLOW'.encode() in response.data
    
    # Les totaux devraient être visibles dans le HTML
    assert '>15<'.encode() in response.data  # Total pour Lignes à sang (10 + 5)
    assert '>5<'.encode() in response.data   # Total pour K7 FLOW (3 + 2)

def test_generate_order(client, init_database):
    # Créer le dossier templates s'il n'existe pas
    templates_dir = os.path.join(os.path.dirname(client.application.instance_path), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Créer un fichier de bon de commande fictif pour le test
    test_doc_path = os.path.join(templates_dir, 'BON COMMANDE PATIENT_KP100225.docx')
    if not os.path.exists(test_doc_path):
        with open(test_doc_path, 'w') as f:
            f.write('Test document')
    
    # Créer quelques produits
    client.post('/api/products', data={'name': 'Lignes à sang', 'quantity': 5, 'location': 'box'})
    client.post('/api/products', data={'name': 'K7 FLOW', 'quantity': 3, 'location': 'apartment'})
    
    # Générer le bon de commande
    response = client.get('/api/generate-order')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert 'BON_COMMANDE_' in response.headers['Content-Disposition']

def test_index_page(client, init_database):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Inventaire'.encode() in response.data
    # Vérifier la présence du tableau récapitulatif
    assert 'Totaux par Produit'.encode() in response.data
    # Vérifier la présence des boutons d'action
    assert 'Exporter CSV'.encode() in response.data
    assert 'Bon de Commande'.encode() in response.data

def test_product_list(client, init_database):
    response = client.get('/')
    # Vérifier que tous les produits disponibles sont dans le select
    for product in AVAILABLE_PRODUCTS:
        assert product.encode() in response.data

def test_product_totals(client, init_database):
    # Ajouter quelques produits
    client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 5,
        'location': 'box'
    })
    client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 3,
        'location': 'apartment'
    })
    
    response = client.get('/')
    # Vérifier que les totaux sont corrects
    assert 'Lignes à sang'.encode() in response.data
    assert '>5<'.encode() in response.data  # Total box
    assert '>3<'.encode() in response.data  # Total apartment
    assert '>8<'.encode() in response.data  # Total global

def test_add_product(client, init_database):
    response = client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 5,
        'location': 'box'
    })
    assert response.status_code == 302
    
    # Vérifier que le produit a été ajouté
    response = client.get('/')
    assert 'Lignes à sang'.encode() in response.data
    assert '>5<'.encode() in response.data

def test_update_product(client, init_database):
    # Créer un produit
    client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 5,
        'location': 'box'
    })
    
    with client.application.app_context():
        product = Product.query.filter_by(name='Lignes à sang').first()
        
        # Mettre à jour le produit
        response = client.put(f'/api/products/{product.id}', json={
            'quantity': 10,
            'location': 'apartment'
        })
        assert response.status_code == 200
        
        # Vérifier la mise à jour
        updated_product = Product.query.get(product.id)
        assert updated_product.quantity == 10
        assert updated_product.location == 'apartment'
        
        # Vérifier l'historique - il devrait y avoir deux entrées
        history_entries = ProductHistory.query.filter_by(product_id=product.id).order_by(ProductHistory.timestamp).all()
        assert len(history_entries) == 2
        
        # Première entrée : création
        assert history_entries[0].action == 'create'
        assert history_entries[0].new_quantity == 5
        assert history_entries[0].new_location == 'box'
        
        # Deuxième entrée : mise à jour
        assert history_entries[1].action == 'update'
        assert history_entries[1].old_quantity == 5
        assert history_entries[1].new_quantity == 10
        assert history_entries[1].old_location == 'box'
        assert history_entries[1].new_location == 'apartment'

def test_delete_product(client, init_database):
    # Créer un produit
    client.post('/api/products', data={
        'name': 'Lignes à sang',
        'quantity': 5,
        'location': 'box'
    })
    
    with client.application.app_context():
        product = Product.query.filter_by(name='Lignes à sang').first()
        
        # Supprimer le produit
        response = client.delete(f'/api/products/{product.id}')
        assert response.status_code == 204
        
        # Vérifier la suppression
        deleted_product = Product.query.get(product.id)
        assert deleted_product is None

def test_reset_inventory(client, init_database):
    # Ajouter des produits
    client.post('/api/products', data={'name': 'Lignes à sang', 'quantity': 5, 'location': 'box'})
    client.post('/api/products', data={'name': 'K7 FLOW', 'quantity': 3, 'location': 'apartment'})
    
    # Réinitialiser l'inventaire
    response = client.post('/api/reset-inventory')
    assert response.status_code == 302
    
    # Vérifier que tous les produits sont à 0
    with client.application.app_context():
        products = Product.query.all()
        for product in products:
            assert product.quantity == 0

def test_export_csv(client, init_database):
    # Ajouter des produits
    client.post('/api/products', data={'name': 'Lignes à sang', 'quantity': 5, 'location': 'box'})
    client.post('/api/products', data={'name': 'K7 FLOW', 'quantity': 3, 'location': 'apartment'})
    
    # Exporter en CSV
    response = client.get('/api/export-csv')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert 'Lignes à sang'.encode() in response.data
    assert 'K7 FLOW'.encode() in response.data

def test_generate_order(client, init_database):
    # Créer le dossier templates s'il n'existe pas
    templates_dir = os.path.join(os.path.dirname(client.application.instance_path), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Créer un fichier de bon de commande fictif pour le test
    test_doc_path = os.path.join(templates_dir, 'BON COMMANDE PATIENT_KP100225.docx')
    if not os.path.exists(test_doc_path):
        with open(test_doc_path, 'w') as f:
            f.write('Test document')
    
    # Ajouter des produits
    client.post('/api/products', data={'name': 'Lignes à sang', 'quantity': 5, 'location': 'box'})
    client.post('/api/products', data={'name': 'K7 FLOW', 'quantity': 3, 'location': 'apartment'})
    
    # Générer le bon de commande
    response = client.get('/api/generate-order')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert 'BON_COMMANDE_' in response.headers['Content-Disposition']
