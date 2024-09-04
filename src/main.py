from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from src.base_models import TranslateRequest, TranslateResponse, Settings


app = FastAPI()
settings = Settings()


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


def get_settings() -> Settings:
    return Settings()


@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest, settings: Settings = Depends(get_settings)):
    if request.model not in settings.models:
        raise HTTPException(status_code=400, detail="Model not supported")

    # Заглушка для перевода
    translated_text = "123"

    response = TranslateResponse(
        text=translated_text,
        time=datetime.now(),
        model=request.model,
        temp=settings.temperature,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )
    return response


@app.get("/config")
def get_config(settings: Settings = settings):
    return {"TEMPERATURE": settings.temperature, "MODELS": settings.models}
