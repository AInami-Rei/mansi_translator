from fastapi import FastAPI, Depends
from src.base_models import TranslateRequest, TranslateResponse, Settings
import requests

app = FastAPI()
settings = Settings()


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


def get_settings() -> Settings:
    return Settings()


@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest, settings: Settings = Depends(get_settings)):
    if request.source_lang == request.target_lang:
        return TranslateResponse(
            text=request.text,
            original_text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

    params = {"text": request.text}
    headers = {"accept": "application/json"}
    url = settings.url + f"/translate/{request.source_lang}-{request.target_lang}"
    response = requests.post(url, params=params, headers=headers).json()

    answer = TranslateResponse(
        text=response["translation"],
        original_text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )
    return answer


@app.get("/config")
def get_config(settings: Settings = settings):
    return {"TEMPERATURE": settings.temperature, "MODELS": settings.models}
