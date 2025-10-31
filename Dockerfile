FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --upgrade pip \
    && pip install "." \
    && rm -rf /root/.cache/pip

EXPOSE 8000

CMD ["uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
