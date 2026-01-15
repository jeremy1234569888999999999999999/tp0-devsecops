import pytest
from unittest.mock import MagicMock, patch
from app import app, items

@pytest.fixture
def client():
    app.config['TESTING'] = True
    items.clear()
    with app.test_client() as client:
        yield client

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'healthy'

def test_add_item_success(client):
    with patch('app.cache') as mock_cache:
        mock_cache.incr = MagicMock()
        r = client.post('/items', json={"name": "Clavier", "quantity": 5})
        assert r.status_code == 201
        assert r.get_json()['name'] == 'Clavier'

def test_add_item_missing_name(client):
    r = client.post('/items', json={"quantity": 5})
    assert r.status_code == 400

def test_get_items(client):
    r = client.get('/items')
    assert r.status_code == 200
    assert 'items' in r.get_json()
