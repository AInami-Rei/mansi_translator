FROM python:3.9-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.8.3

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl=7.88.1-10+deb12u7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl --version
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY src src

FROM python:3.9-slim as runner

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
