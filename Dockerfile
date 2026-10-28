FROM ghcr.io/astral-sh/uv:0.13.5 AS uv

FROM python:3.13.17-slim-bookworm AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# model/ is gitignored, so train it during the build with the same locked
# scikit-learn/skops versions the API will load it with.
FROM base AS trainer

COPY src ./src
COPY data/King_County_House_prices_dataset.csv ./data/
RUN uv run --no-sync python -m src.data_pipeline --model basic

FROM base AS runtime

COPY src ./src
COPY app ./app
COPY --from=trainer /app/model/basic_model.bin ./model/

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
