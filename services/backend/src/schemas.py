from pydantic import BaseModel
from typing import List
from datetime import date

class Segmentacao(BaseModel):
    name: str
    original: str
    mask: str
    area: float
    data: date

class Grupo(BaseModel):
    images: List[Segmentacao]
