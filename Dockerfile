# Build the scraper from its locked Python dependencies.
FROM python:3.11-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir uv==0.13.0

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY main.py ./

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["python", "main.py"]
