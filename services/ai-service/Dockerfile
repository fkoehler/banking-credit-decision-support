FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /usr/local/bin/uv
WORKDIR /app
COPY services/ai-service/pyproject.toml services/ai-service/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY services/ai-service/src src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
RUN useradd --system --uid 10001 app
WORKDIR /app
COPY --from=build /app /app
USER 10001
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8081
CMD ["uvicorn", "bank_ai.main:app", "--host", "0.0.0.0", "--port", "8081"]
