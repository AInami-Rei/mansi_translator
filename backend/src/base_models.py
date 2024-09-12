from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Literal


class TranslateRequest(BaseModel):
    """
    Translation request schema
    """

    text: str
    source_lang: Literal["ms", "ru"]
    target_lang: Literal["ms", "ru"]


class TranslateResponse(BaseModel):
    """
    Translation response schema
    """

    text: str
    original_text: str
    source_lang: Literal["ms", "ru"]
    target_lang: Literal["ms", "ru"]


class Settings(BaseSettings):
    """
    App settings
    """

    url: str

    class Config:
        env_file = ".env"
