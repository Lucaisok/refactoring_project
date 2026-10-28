import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from src.modeling import MODEL_CONFIGS

VALID_HOUSE = {
    "bedrooms": 3,
    "bathrooms": 2.0,
    "sqft_living": 1800,
    "sqft_lot": 5000,
    "floors": 1.0,
}


@pytest.fixture(scope="module")
def client():
    # The context manager runs the lifespan, so the model is loaded.
    with TestClient(app) as c:
        yield c


def test_predict_returns_positive_price(client):
    response = client.post("/prediction", json=VALID_HOUSE)

    assert response.status_code == 200
    assert response.json()["price"] > 0


def test_predict_matches_model_directly(client):
    response = client.post("/prediction", json=VALID_HOUSE)

    features = list(MODEL_CONFIGS["basic"].features)
    expected = app.state.model.predict(pd.DataFrame([VALID_HOUSE], columns=features))[0]
    assert response.json()["price"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "field, value",
    [
        ("bedrooms", 0),
        ("bathrooms", 0),
        ("sqft_living", -100),
        ("floors", 10),
    ],
)
def test_predict_rejects_out_of_range_values(client, field, value):
    response = client.post("/prediction", json={**VALID_HOUSE, field: value})

    assert response.status_code == 422


def test_predict_rejects_missing_fields(client):
    response = client.post("/prediction", json={"bedrooms": 3})

    assert response.status_code == 422
