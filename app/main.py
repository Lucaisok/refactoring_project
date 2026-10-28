from contextlib import asynccontextmanager

import pandas as pd
import skops.io as sio
from fastapi import FastAPI, Request

from app.schemas import HouseFeatures, PricePrediction
from src.modeling import MODEL_CONFIGS


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = MODEL_CONFIGS["basic"]
    if not config.path.exists():
        raise RuntimeError(
            f"Model not found at {config.path}. "
            "Run `python -m src.data_pipeline --model basic` first."
        )

    model = sio.load(config.path)
    if list(model.feature_names_in_) != list(config.features):
        raise RuntimeError("Saved model features don't match the config; retrain it.")

    app.state.model = model
    yield
    # Code after `yield` runs on shutdown; nothing to clean up here.


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_root():
    return {"message": "Hello World"}


@app.post("/prediction")
def get_price(house_features: HouseFeatures, request: Request) -> PricePrediction:
    model = request.app.state.model
    df = pd.DataFrame(
        [house_features.model_dump()], columns=list(MODEL_CONFIGS["basic"].features)
    )
    price_prediction = model.predict(df)[0]
    return PricePrediction(price=round(float(price_prediction), 2))
