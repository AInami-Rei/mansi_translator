from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

available_language_directions = ["ms-ru", "ru-ms"]


class MySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


class ServiceSettings(MySettings):
    default_device: str = Field("cuda:0")
    ms_ru_model_maxlen: int = 256
    ms_ru_model_name: str = Field(default="/models/mbart-600m-v1")
    ru_ms_model_maxlen: int = 256
    ru_ms_model_name: str = Field(default="/models/mbart-600m-v2")
