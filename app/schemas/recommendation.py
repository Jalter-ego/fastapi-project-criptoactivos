from pydantic import BaseModel

class PredictionState(BaseModel):
    balance: float
    crypto_held: float