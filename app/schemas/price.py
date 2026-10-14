from pydantic import BaseModel, ConfigDict

class PriceResponse(BaseModel):
    id: int
    ticker: str
    price: float
    timestamp: int

    model_config = ConfigDict(from_attributes=True)