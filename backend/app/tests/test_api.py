import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config.database import Base, get_db
from app.models.models import Asset

# Test Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    # Seed a test asset
    db = TestingSessionLocal()
    test_asset = Asset(
        id="test_bridge_99",
        name="Test Gateway Bridge",
        type="Bridge",
        location="Sector Testing",
        owner="Testing Authority",
        construction_material="Steel",
        age_years=5,
        gis_latitude=35.0,
        gis_longitude=-115.0,
        health_score=95.0,
        rul_months=240.0,
        status="Healthy"
    )
    db.add(test_asset)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["platform"] == "InfraMind AI"

def test_list_assets():
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["id"] == "test_bridge_99"

def test_predict_asset():
    response = client.get("/api/v1/predict?asset_id=test_bridge_99")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["asset_id"] == "test_bridge_99"
    assert "risk_score" in json_data
    assert "failure_classification" in json_data

def test_explain_prediction():
    response = client.get("/api/v1/explain?asset_id=test_bridge_99")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["asset_id"] == "test_bridge_99"
    assert "shap_values" in json_data
    assert "explanation_text" in json_data

def test_disaster_simulation():
    req_body = {
        "disaster_type": "Earthquake",
        "gis_latitude": 35.0,
        "gis_longitude": -115.0,
        "radius_km": 10.0,
        "intensity": 6.5
    }
    response = client.post("/api/v1/disaster/simulate", json=req_body)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["disaster_type"] == "Earthquake"
    assert json_data["population_impacted"] > 0
    assert len(json_data["affected_assets"]) >= 1
