from pydantic import BaseModel


class Iris(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float
    Species: str
