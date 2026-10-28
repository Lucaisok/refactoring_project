from pydantic import BaseModel, Field


class HouseFeatures(BaseModel):
    bedrooms: int = Field(ge=1, le=15)
    bathrooms: float = Field(gt=0, le=10)
    sqft_living: int = Field(gt=0)
    sqft_lot: int = Field(gt=0)
    floors: float = Field(ge=1, le=4)


class PricePrediction(BaseModel):
    price: float
