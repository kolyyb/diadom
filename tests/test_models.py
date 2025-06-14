import pytest
from app import create_app, db
from app.models import Product

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_new_product(app):
    with app.app_context():
        product = Product(
            name='Lignes à sang',
            quantity=10,
            location='box'
        )
        db.session.add(product)
        db.session.commit()

        assert product.id is not None
        assert product.name == 'Lignes à sang'
        assert product.quantity == 10
        assert product.location == 'box'

def test_product_location_validation(app):
    with app.app_context():
        with pytest.raises(ValueError) as excinfo:
            Product(
                name='K7 Ergo Flow',
                quantity=5,
                location='invalid_location'  # Location invalide
            )
        assert "Location must be one of: box, apartment" in str(excinfo.value)
