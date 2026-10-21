FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY main.py ./

RUN pip install -e .

LABEL org.opencontainers.image.source="https://github.com/n4mlz/st4r8ux-scraper"

CMD ["python", "main.py"]
