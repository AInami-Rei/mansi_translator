import settings
import torch
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from ray import serve
from starlette.status import HTTP_400_BAD_REQUEST
from transformers import MBartForConditionalGeneration, MBart50Tokenizer

app = FastAPI(title="Translator")

service_settings = settings.ServiceSettings()


class TranslationResult(BaseModel):
    original_text: str
    translation: str


def init_model_tokenizer(model_name: str, device: str):
    model = MBartForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        load_in_8bit=True,
    )

    model = torch.compile(model)
    tokenizer = MBart50Tokenizer.from_pretrained(model_name)
    old_len = len(tokenizer)
    tokenizer.lang_code_to_id["mans_XX"] = old_len - 1
    tokenizer.id_to_lang_code[old_len - 1] = "mans_XX"
    tokenizer.fairseq_tokens_to_ids["<mask>"] = (
        len(tokenizer.sp_model)
        + len(tokenizer.lang_code_to_id)
        + tokenizer.fairseq_offset
    )
    tokenizer.fairseq_tokens_to_ids.update(tokenizer.lang_code_to_id)
    tokenizer.fairseq_ids_to_tokens = {
        v: k for k, v in tokenizer.fairseq_tokens_to_ids.items()
    }
    if "mans_XX" not in tokenizer._additional_special_tokens:
        tokenizer._additional_special_tokens.append("mans_XX")

    return model, tokenizer


def gen_translate(
    model,
    tokenizer,
    text: str,
    src: str,
    trg: str,
    max_length: str = 200,
    num_beams: str = 5,
    repetition_penalty: float = 5.0,
    **kwargs,
) -> str:
    tokenizer.src_lang = src
    tokenizer.tgt_lang = trg

    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded.to(model.device),
        forced_bos_token_id=tokenizer.lang_code_to_id[trg],
        max_length=max_length,
        num_beams=num_beams,
        repetition_penalty=repetition_penalty,
    )

    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]


@serve.deployment()
@serve.ingress(app)
class Translator:
    def __init__(self):
        # Load models
        ru_ms_model, ru_ms_tokenizer = init_model_tokenizer(
            service_settings.ru_ms_model_name, service_settings.default_device
        )
        ms_ru_model, ms_ru_tokenizer = init_model_tokenizer(
            service_settings.ms_ru_model_name, service_settings.default_device
        )

        self.models = {"ru-ms": ru_ms_model, "ms-ru": ms_ru_model}
        self.tokenizers = {"ru-ms": ru_ms_tokenizer, "ms-ru": ms_ru_tokenizer}
        self.maxlen = {
            "ru-ms": service_settings.ru_ms_model_maxlen,
            "ms-ru": service_settings.ms_ru_model_maxlen,
        }

        self.rutok = "ru_RU"
        self.mansitok = "mans_XX"

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

        model_output = gen_translate(
            model=self.models[direction],
            tokenizer=self.tokenizers[direction],
            text=text,
            src=self.rutok if direction == "ru_ms" else self.mansitok,
            trg=self.rutok if direction == "ms_ru" else self.mansitok,
            max_length=self.maxlen[direction],
        )

        return TranslationResult(original_text=text, translation=model_output)

    @app.get("/")
    async def root(self):
        """Redirec to docs by default"""
        return RedirectResponse("/docs")


translator_app = Translator.bind()
