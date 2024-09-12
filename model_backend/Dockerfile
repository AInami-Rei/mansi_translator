FROM huecker.io/library/python:3.11

ENV DST=/usr/src/app/ \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.8.1 \
    PYTHONPATH="/usr/src/app/src/common"

WORKDIR ${DST}

RUN pip3 install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --only main --no-interaction --no-root
RUN mkdir -p /data && mkdir -p /opt/app

WORKDIR /opt/app
COPY ray_config.yaml .
COPY src/* .

CMD ["serve", "run", "ray_config.yaml"]
