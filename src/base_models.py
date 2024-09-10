from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Literal


class TranslateRequest(BaseModel):
    text: str
    source_lang: Literal["ms", "ru"]
    target_lang: Literal["ms", "ru"]


class TranslateResponse(BaseModel):
    text: str
    original_text: str
    source_lang: str
    target_lang: str


class Settings(BaseSettings):
    url: str

    class Config:
        env_file = ".env"
