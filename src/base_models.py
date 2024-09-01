from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Literal
from datetime import datetime


class TranslateRequest(BaseModel):
    text: str
    source_lang: Literal["mansi", "ru"]
    target_lang: Literal["mansi", "ru"]
    model: str


class TranslateResponse(BaseModel):
    text: str
    time: datetime
    model: str
    temp: float
    source_lang: str
    target_lang: str


class Settings(BaseSettings):
    temperature: float
    models: str

    class Config:
        env_file = ".env"
