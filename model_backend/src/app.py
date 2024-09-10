import settings
import torch
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from ray import serve
from starlette.status import HTTP_400_BAD_REQUEST
from transformers import pipeline

app = FastAPI(title="Translator")

service_settings = settings.ServiceSettings()


class TranslationResult(BaseModel):
    original_text: str
    translation: str


def create_pipeline(language_direction, model_name, device, max_length):
    return pipeline(
        f"translation_{language_direction}",
        model=model_name,
        device=torch.device(device),
        max_length=max_length,
    )


@serve.deployment()
@serve.ingress(app)
class Translator:
    def __init__(self):
        # Load models
        self.pipelines = {
            "ru-ms": create_pipeline(
                "ru_to_ms",
                service_settings.ru_ms_model_name,
                service_settings.default_device,
                service_settings.ru_ms_model_maxlen,
            ),
            "ms-ru": create_pipeline(
                "ms_to_ru",
                service_settings.ms_ru_model_name,
                service_settings.default_device,
                service_settings.ms_ru_model_maxlen,
            ),
        }

    @app.post("/translate/{direction}", tags=["translator"])
    async def translate(
        self,
        direction: str = Path(
            ...,
            enum=settings.available_language_directions,
            description="The translation direction, either ms-ru  or ru-ms",
        ),
        text: str = Query(..., description="The text to be translated"),
    ) -> TranslationResult:
        """Translate text between Mansi and Russian."""
        if direction not in settings.available_language_directions:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Wrong direction parametr"
            )

        translation_model = self.pipelines[direction]
        model_output = translation_model(text)

        translation = model_output[0]["translation_text"]

        return TranslationResult(original_text=text, translation=translation)

    @app.get("/")
    async def root(self):
        """Redirec to docs by default"""
        return RedirectResponse("/docs")


translator_app = Translator.bind()
